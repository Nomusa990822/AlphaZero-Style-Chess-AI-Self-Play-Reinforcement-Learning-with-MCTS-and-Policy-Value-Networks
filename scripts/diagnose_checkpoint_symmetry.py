"""Read-only colour-symmetry and self-play audit for preserved checkpoints.

The audit compares each checkpoint with its own colour-swapped, vertically
mirrored positions and plays each checkpoint against itself over the fixed
mirrored opening suite. It does not train, alter, or promote checkpoints.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import chess
import numpy as np

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTS, MCTSConfig
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import load_checkpoint
from src.training.evaluator import NetworkEvaluator
from src.training.tactical_benchmark import load_tactical_positions


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_agent(checkpoint: Path, encoding: MoveEncoding, encoder: BoardEncoder):
    network = AlphaZeroNet(
        action_size=encoding.action_size,
        config=NetworkConfig(
            input_channels=20,
            board_size=8,
            num_filters=64,
            num_res_blocks=3,
            value_hidden_size=128,
        ),
    )
    payload = load_checkpoint(checkpoint, network, optimizer=None, map_location="cpu")
    network.eval()
    inference = ModelInference(network, encoding, encoder, device="cpu")
    metadata = {
        "filename": checkpoint.name,
        "size_bytes": checkpoint.stat().st_size,
        "sha256": sha256_file(checkpoint),
        "epoch": payload.get("epoch"),
        "extra": payload.get("extra", {}),
    }
    return inference, metadata


def legal_policy_distribution(
    board: chess.Board,
    probabilities: np.ndarray,
    encoding: MoveEncoding,
) -> dict[str, float]:
    values = {
        move.uci(): float(probabilities[encoding.move_to_tensor_index(move, board)])
        for move in board.legal_moves
    }
    total = sum(values.values())
    if total <= 0.0:
        uniform = 1.0 / len(values)
        return {move: uniform for move in values}
    return {move: value / total for move, value in values.items()}


def mirror_move_uci(move_uci: str) -> str:
    """Map a UCI move through the vertical reflection used by Board.mirror()."""
    move = chess.Move.from_uci(move_uci)
    return chess.Move(
        chess.square_mirror(move.from_square),
        chess.square_mirror(move.to_square),
        promotion=move.promotion,
        drop=move.drop,
    ).uci()


def jensen_shannon_divergence(
    left: dict[str, float],
    right: dict[str, float],
) -> float:
    """JSD in nats for two distributions over the same mapped legal moves."""
    keys = sorted(set(left) | set(right))
    p = np.asarray([left.get(key, 0.0) for key in keys], dtype=np.float64)
    q = np.asarray([right.get(key, 0.0) for key in keys], dtype=np.float64)
    p_sum, q_sum = float(p.sum()), float(q.sum())
    if p_sum <= 0.0 or q_sum <= 0.0:
        raise ValueError("Policy distributions must have positive mass.")
    p /= p_sum
    q /= q_sum
    midpoint = 0.5 * (p + q)
    p_mask, q_mask = p > 0, q > 0
    kl_pm = float(np.sum(p[p_mask] * np.log(p[p_mask] / midpoint[p_mask])))
    kl_qm = float(np.sum(q[q_mask] * np.log(q[q_mask] / midpoint[q_mask])))
    return 0.5 * (kl_pm + kl_qm)


def inspect_mirror_pair(
    inference: ModelInference,
    encoding: MoveEncoding,
    case,
    simulations: int,
) -> dict[str, Any]:
    board = chess.Board(case.fen)
    mirrored = board.mirror()
    mirrored_acceptable = {
        mirror_move_uci(uci) for uci in case.acceptable_moves
    }

    base_probs, base_value = inference.predict(board)
    mirror_probs, mirror_value = inference.predict(mirrored)
    base_policy = legal_policy_distribution(board, base_probs, encoding)
    mirror_policy = legal_policy_distribution(mirrored, mirror_probs, encoding)
    mapped_base_policy = {
        mirror_move_uci(move): probability
        for move, probability in base_policy.items()
    }
    base_policy_top = sorted(
        base_policy, key=lambda move: (-base_policy[move], move)
    )[0]
    mirror_policy_top = sorted(
        mirror_policy, key=lambda move: (-mirror_policy[move], move)
    )[0]

    config = MCTSConfig(
        num_simulations=simulations,
        add_dirichlet_noise=False,
        temperature=0.0,
        use_tactical_root_filter=True,
        use_static_exchange_ordering=True,
    )
    base_search = MCTS(inference, encoding, config)
    mirror_search = MCTS(inference, encoding, config)
    base_root = base_search.run(board)
    mirror_root = mirror_search.run(mirrored)
    base_selected = base_search.select_action(base_root, temperature=0.0)
    mirror_selected = mirror_search.select_action(mirror_root, temperature=0.0)
    expected_mirror_selected = chess.Move.from_uci(
        mirror_move_uci(base_selected.uci())
    )

    return {
        "position_id": case.position_id,
        "motif": case.motif,
        "original_side_to_move": "white" if board.turn == chess.WHITE else "black",
        "mirrored_side_to_move": "white" if mirrored.turn == chess.WHITE else "black",
        "original_acceptable_moves": sorted(case.acceptable_moves),
        "mirrored_acceptable_moves": sorted(mirrored_acceptable),
        "original_policy_top1": base_policy_top,
        "mirrored_policy_top1": mirror_policy_top,
        "policy_top1_mirror_agreement": (
            mirror_policy_top == mirror_move_uci(base_policy_top)
        ),
        "policy_js_divergence_nats": jensen_shannon_divergence(
            mapped_base_policy, mirror_policy
        ),
        "original_raw_value": base_value,
        "mirrored_raw_value": mirror_value,
        "absolute_raw_value_difference": abs(base_value - mirror_value),
        "original_mcts_move": base_selected.uci(),
        "mirrored_mcts_move": mirror_selected.uci(),
        "expected_mirrored_mcts_move": expected_mirror_selected.uci(),
        "mcts_mirror_agreement": mirror_selected == expected_mirror_selected,
        "original_mcts_acceptable": base_selected.uci() in case.acceptable_moves,
        "mirrored_mcts_acceptable": mirror_selected.uci() in mirrored_acceptable,
    }


def summarise_pairs(records: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(records)
    return {
        "mirrored_position_pairs": count,
        "policy_top1_mirror_agreement_count": sum(
            record["policy_top1_mirror_agreement"] for record in records
        ),
        "policy_top1_mirror_agreement_rate": sum(
            record["policy_top1_mirror_agreement"] for record in records
        ) / count,
        "mcts_mirror_agreement_count": sum(
            record["mcts_mirror_agreement"] for record in records
        ),
        "mcts_mirror_agreement_rate": sum(
            record["mcts_mirror_agreement"] for record in records
        ) / count,
        "mean_policy_js_divergence_nats": float(np.mean([
            record["policy_js_divergence_nats"] for record in records
        ])),
        "mean_absolute_raw_value_difference": float(np.mean([
            record["absolute_raw_value_difference"] for record in records
        ])),
        "original_mcts_acceptable": sum(
            record["original_mcts_acceptable"] for record in records
        ),
        "mirrored_mcts_acceptable": sum(
            record["mirrored_mcts_acceptable"] for record in records
        ),
    }


def self_play_symmetry(
    inference: ModelInference,
    encoding: MoveEncoding,
    simulations: int,
    games: int,
) -> dict[str, Any]:
    evaluator = NetworkEvaluator(
        move_encoding=encoding,
        mcts_config=MCTSConfig(
            num_simulations=simulations,
            add_dirichlet_noise=False,
            temperature=0.0,
        ),
    )
    result = evaluator.compare_models(inference, inference, num_games=games)
    return {
        "games_played": result.games_played,
        "opening_pairs": len(result.opening_pair_scores),
        "wins": result.wins,
        "losses": result.losses,
        "draws": result.draws,
        "designated_model_score": result.score,
        "model_as_white": {
            "wins": result.candidate_white_wins,
            "losses": result.candidate_white_losses,
            "draws": result.candidate_white_draws,
        },
        "model_as_black": {
            "wins": result.candidate_black_wins,
            "losses": result.candidate_black_losses,
            "draws": result.candidate_black_draws,
        },
        "opening_pair_results": list(result.opening_pair_results),
        "interpretation": (
            "Same checkpoint controls both colours; results diagnose "
            "colour/mirror consistency, not playing strength."
        ),
    }


def inspect_checkpoint(
    path: Path,
    cases,
    encoding: MoveEncoding,
    encoder: BoardEncoder,
    tactical_simulations: int,
    self_play_simulations: int,
    self_play_games: int,
) -> dict[str, Any]:
    inference, metadata = build_agent(path, encoding, encoder)
    records = [
        inspect_mirror_pair(inference, encoding, case, tactical_simulations)
        for case in cases
    ]
    return {
        "checkpoint": metadata,
        "mirror_summary": summarise_pairs(records),
        "mirror_pairs": records,
        "self_play_colour_symmetry": self_play_symmetry(
            inference, encoding, self_play_simulations, self_play_games
        ),
    }


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument(
        "--positions", default="benchmarks/tactical_positions.jsonl"
    )
    parser.add_argument("--tactical-simulations", type=int, default=25)
    parser.add_argument("--self-play-simulations", type=int, default=50)
    parser.add_argument("--self-play-games", type=int, default=24)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.tactical_simulations < 1 or args.self_play_simulations < 1:
        parser.error("simulation counts must be positive")
    if (
        args.self_play_games < 2
        or args.self_play_games % 2
        or args.self_play_games > 24
    ):
        parser.error(
            "self-play games must be even and between 2 and 24 (12 opening pairs)"
        )
    return args


def main():
    args = parse_args()
    baseline = Path(args.baseline)
    candidate = Path(args.candidate)
    for path in (baseline, candidate):
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Checkpoint missing or empty: {path}")

    encoding = MoveEncoding()
    encoder = BoardEncoder()
    positions = load_tactical_positions(args.positions)
    report = {
        "schema_version": 1,
        "evaluation": "checkpoint_colour_mirror_and_self_play_symmetry",
        "settings": {
            "device": "cpu",
            "tactical_simulations": args.tactical_simulations,
            "self_play_simulations": args.self_play_simulations,
            "self_play_games_per_checkpoint": args.self_play_games,
            "self_play_opening_suite": "benchmarks/evaluation_openings.jsonl",
            "tactical_positions": len(positions),
            "mirror_transform": (
                "python-chess Board.mirror(): vertical reflection plus colour swap"
            ),
            "dirichlet_noise": False,
            "temperature": 0.0,
        },
        "baseline": inspect_checkpoint(
            baseline, positions, encoding, encoder, args.tactical_simulations,
            args.self_play_simulations, args.self_play_games,
        ),
        "candidate": inspect_checkpoint(
            candidate, positions, encoding, encoder, args.tactical_simulations,
            args.self_play_simulations, args.self_play_games,
        ),
        "interpretation_limits": [
            "Mirror agreement measures internal colour-symmetry consistency, not tactical correctness.",
            "The self-play colour audit pits a checkpoint against itself; it is not a strength comparison.",
            "Raw value mirror differences are consistency measurements, not value calibration against game outcomes.",
            "The curated tactical corpus and 12-opening suite are small fixed diagnostic sets, not an Elo benchmark.",
        ],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"Saved colour-symmetry report: {output}")


if __name__ == "__main__":
    main()
