"""Inspect raw policy, value predictions and MCTS decisions on curated positions."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import chess

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTS, MCTSConfig
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import load_checkpoint
from src.training.tactical_benchmark import load_tactical_positions


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def legal_policy_ranking(board: chess.Board, probabilities, encoding: MoveEncoding) -> list[dict[str, Any]]:
    legal = []
    for move in board.legal_moves:
        index = encoding.move_to_tensor_index(move, board)
        legal.append((move, float(probabilities[index])))
    total = sum(prob for _, prob in legal)
    if total > 0:
        legal = [(move, prob / total) for move, prob in legal]
    legal.sort(key=lambda item: (-item[1], item[0].uci()))
    return [{"move": move.uci(), "probability": probability} for move, probability in legal]


def build_agent(checkpoint: Path, simulations: int):
    encoding = MoveEncoding()
    network = AlphaZeroNet(
        action_size=encoding.action_size,
        config=NetworkConfig(
            input_channels=20, board_size=8, num_filters=64,
            num_res_blocks=3, value_hidden_size=128,
        ),
    )
    payload = load_checkpoint(checkpoint, network, optimizer=None, map_location="cpu")
    network.eval()
    inference = ModelInference(network, encoding, BoardEncoder(), device="cpu")
    search = MCTS(
        inference, encoding,
        MCTSConfig(
            num_simulations=simulations,
            add_dirichlet_noise=False,
            temperature=0.0,
            use_tactical_root_filter=True,
            use_static_exchange_ordering=True,
        ),
    )
    metadata = {
        "filename": checkpoint.name,
        "size_bytes": checkpoint.stat().st_size,
        "sha256": sha256_file(checkpoint),
        "epoch": payload.get("epoch"),
        "extra": payload.get("extra", {}),
        "architecture": {
            "input_channels": 20, "board_size": 8, "num_filters": 64,
            "num_res_blocks": 3, "value_hidden_size": 128,
            "action_size": encoding.action_size,
        },
    }
    return inference, search, encoding, metadata


def inspect_checkpoint(checkpoint: Path, positions, simulations: int, top_k: int) -> dict[str, Any]:
    inference, search, encoding, metadata = build_agent(checkpoint, simulations)
    records = []
    for case in positions:
        board = chess.Board(case.fen)
        probabilities, value = inference.predict(board)
        ranking = legal_policy_ranking(board, probabilities, encoding)
        root = search.run(board)
        selected = search.select_action(root, temperature=0.0)
        children = sorted(
            root.children.values(),
            key=lambda child: (-child.visit_count, child.move.uci()),
        )
        visits = sum(child.visit_count for child in children)
        visit_ranking = [
            {
                "move": child.move.uci(),
                "visits": child.visit_count,
                "visit_fraction": child.visit_count / visits if visits else 0.0,
                "mean_q": child.q_value,
            }
            for child in children[:top_k]
        ]
        accepted = sorted(case.acceptable_moves)
        records.append({
            "id": case.position_id,
            "motif": case.motif,
            "phase": case.phase,
            "side_to_move": "white" if board.turn == chess.WHITE else "black",
            "fen": case.fen,
            "acceptable_moves": accepted,
            "raw_value_side_to_move": value,
            "policy_top_k_legal": ranking[:top_k],
            "policy_top1_acceptable": bool(ranking and ranking[0]["move"] in accepted),
            "mcts_selected_move": selected.uci(),
            "mcts_selected_acceptable": selected.uci() in accepted,
            "mcts_top_k_visits": visit_ranking,
            "legal_move_count": board.legal_moves.count(),
        })

    total = len(records)
    policy_hits = sum(record["policy_top1_acceptable"] for record in records)
    mcts_hits = sum(record["mcts_selected_acceptable"] for record in records)
    values = [record["raw_value_side_to_move"] for record in records]
    by_motif: dict[str, dict[str, int]] = {}
    for record in records:
        group = by_motif.setdefault(record["motif"], {"total": 0, "policy_hits": 0, "mcts_hits": 0})
        group["total"] += 1
        group["policy_hits"] += int(record["policy_top1_acceptable"])
        group["mcts_hits"] += int(record["mcts_selected_acceptable"])
    return {
        "checkpoint": metadata,
        "summary": {
            "positions": total,
            "policy_top1_hits": policy_hits,
            "policy_top1_accuracy": policy_hits / total if total else 0.0,
            "mcts_hits": mcts_hits,
            "mcts_accuracy": mcts_hits / total if total else 0.0,
            "mean_raw_value_side_to_move": sum(values) / len(values) if values else 0.0,
            "minimum_raw_value": min(values) if values else None,
            "maximum_raw_value": max(values) if values else None,
            "by_motif": by_motif,
        },
        "positions": records,
    }


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--positions", default="benchmarks/tactical_positions.jsonl")
    parser.add_argument("--simulations", type=int, default=25)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.simulations < 1 or args.top_k < 1:
        parser.error("simulations and top-k must be positive")
    return args


def main():
    args = parse_args()
    baseline = Path(args.baseline)
    candidate = Path(args.candidate)
    for path in (baseline, candidate):
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Checkpoint missing or empty: {path}")
    positions = load_tactical_positions(args.positions)
    report = {
        "schema_version": 1,
        "evaluation": "checkpoint_policy_value_mcts_diagnostics",
        "settings": {
            "device": "cpu", "simulations": args.simulations,
            "top_k": args.top_k, "dirichlet_noise": False,
            "temperature": 0.0, "tactical_root_filter": True,
            "static_exchange_ordering": True,
        },
        "baseline_random_initialisation": inspect_checkpoint(
            baseline, positions, args.simulations, args.top_k
        ),
        "candidate_after_one_pilot_iteration": inspect_checkpoint(
            candidate, positions, args.simulations, args.top_k
        ),
        "interpretation_limits": [
            "The curated tactical corpus is small and is not a general playing-strength benchmark.",
            "A raw value prediction is reported from the side-to-move perspective; tactical positions have no independent game-outcome value labels, so value accuracy is not calculated.",
            "Policy top-1 and MCTS acceptable-move rates are separate diagnostic measures, not Elo estimates.",
            "The same checkpoint architecture, corpus, search settings and CPU execution are used for both models.",
        ],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"Saved diagnostics: {output}")


if __name__ == "__main__":
    main()
