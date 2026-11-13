"""Run a paired tactical-root-filter ablation against one checkpoint.

Both search configurations share one loaded model, inference wrapper, corpus,
device and simulation budget. This is a diagnostic benchmark, not an Elo test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter

import chess
import torch

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTS, MCTSConfig
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import load_checkpoint
from src.training.tactical_benchmark import evaluate_tactical_selector, load_tactical_positions


def resolve_device(requested: str) -> torch.device:
    if requested != "auto":
        device = torch.device(requested)
        if device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is unavailable.")
        if device.type == "mps" and not (
            hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        ):
            raise RuntimeError("MPS was requested but is unavailable.")
        return device
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare tactical-root-filter on/off using one checkpoint."
    )
    parser.add_argument("--checkpoint", required=True, help="Compatible model checkpoint.")
    parser.add_argument(
        "--positions",
        default="benchmarks/tactical_positions.jsonl",
        help="JSONL tactical corpus path.",
    )
    parser.add_argument("--simulations", type=int, default=100)
    parser.add_argument("--device", default="auto", help="cpu, cuda, mps, or auto.")
    parser.add_argument("--output", required=True, help="Paired JSON report path.")
    args = parser.parse_args()
    if args.simulations < 1:
        parser.error("--simulations must be at least 1.")
    return args


def main() -> None:
    args = parse_args()
    checkpoint_path = Path(args.checkpoint)
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
    positions = load_tactical_positions(args.positions)
    device = resolve_device(args.device)
    checkpoint_sha256 = hashlib.sha256(checkpoint_path.read_bytes()).hexdigest()

    encoding = MoveEncoding()
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
    payload = load_checkpoint(checkpoint_path, network, optimizer=None, map_location=device)
    inference = ModelInference(
        model=network,
        move_encoding=encoding,
        encoder=BoardEncoder(),
        device=device,
    )

    searches = {
        "filter_on": MCTS(
            inference=inference,
            move_encoding=encoding,
            config=MCTSConfig(
                num_simulations=args.simulations,
                add_dirichlet_noise=False,
                temperature=0.0,
                use_tactical_root_filter=True,
            ),
        ),
        "filter_off": MCTS(
            inference=inference,
            move_encoding=encoding,
            config=MCTSConfig(
                num_simulations=args.simulations,
                add_dirichlet_noise=False,
                temperature=0.0,
                use_tactical_root_filter=False,
            ),
        ),
    }

    selected_by_mode: dict[str, dict[str, str]] = {
        "filter_on": {},
        "filter_off": {},
    }
    per_position = []
    elapsed = {"filter_on": 0.0, "filter_off": 0.0}

    for case in positions:
        board = chess.Board(case.fen)
        row = {
            "id": case.position_id,
            "motif": case.motif,
            "color_to_move": "white" if board.turn == chess.WHITE else "black",
            "phase": case.phase,
            "acceptable_moves": sorted(case.acceptable_moves),
        }
        for mode, search in searches.items():
            started = perf_counter()
            root = search.run(board.copy(stack=True))
            move = search.select_action(root, temperature=0.0)
            duration = perf_counter() - started
            elapsed[mode] += duration
            selected_uci = move.uci()
            selected_by_mode[mode][case.fen] = selected_uci
            row[mode] = {
                "selected_move": selected_uci,
                "correct": selected_uci in case.acceptable_moves,
                "elapsed_seconds": round(duration, 6),
            }
        row["selection_changed"] = (
            row["filter_on"]["selected_move"] != row["filter_off"]["selected_move"]
        )
        per_position.append(row)

    summaries = {}
    for mode in ("filter_on", "filter_off"):
        lookup = selected_by_mode[mode]
        result = evaluate_tactical_selector(
            positions,
            lambda board, moves=lookup: moves[board.fen()],
        )
        summaries[mode] = {
            "total": result.total,
            "correct": result.correct,
            "illegal": result.illegal,
            "accuracy": result.accuracy,
            "by_motif": result.by_motif,
            "by_color": result.by_color,
            "by_phase": result.by_phase,
            "failures": list(result.failures),
            "elapsed_seconds": round(elapsed[mode], 6),
        }

    on_accuracy = summaries["filter_on"]["accuracy"]
    off_accuracy = summaries["filter_off"]["accuracy"]
    report = {
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": checkpoint_sha256,
        "checkpoint_epoch": payload.get("epoch"),
        "corpus": str(args.positions),
        "device": str(device),
        "simulations_per_position": args.simulations,
        "dirichlet_noise": False,
        "selection_temperature": 0.0,
        "paired": True,
        "summary": summaries,
        "comparison": {
            "accuracy_delta_filter_on_minus_off": on_accuracy - off_accuracy,
            "positions_with_changed_selection": sum(
                row["selection_changed"] for row in per_position
            ),
            "positions_filter_on_correct_filter_off_incorrect": sum(
                row["filter_on"]["correct"] and not row["filter_off"]["correct"]
                for row in per_position
            ),
            "positions_filter_off_correct_filter_on_incorrect": sum(
                row["filter_off"]["correct"] and not row["filter_on"]["correct"]
                for row in per_position
            ),
        },
        "positions": per_position,
        "interpretation_limit": (
            "A small curated tactical corpus is diagnostic only; this result is "
            "not an Elo estimate or proof of general playing-strength improvement."
        ),
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered + "\n", encoding="utf-8")
    print(f"Saved paired benchmark report: {output_path}")


if __name__ == "__main__":
    main()
