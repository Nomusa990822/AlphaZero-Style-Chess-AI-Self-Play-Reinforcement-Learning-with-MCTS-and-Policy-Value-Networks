"""Evaluate a trained checkpoint on the curated tactical benchmark corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

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
        description="Score an AlphaZero-style checkpoint on curated tactical positions."
    )
    parser.add_argument("--checkpoint", required=True, help="Model checkpoint path.")
    parser.add_argument(
        "--positions",
        default="benchmarks/tactical_positions.jsonl",
        help="JSONL tactical corpus path.",
    )
    parser.add_argument("--simulations", type=int, default=100)
    parser.add_argument("--device", default="auto", help="cpu, cuda, mps, or auto.")
    parser.add_argument("--output", help="Optional path for a JSON results report.")
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
    search = MCTS(
        inference=inference,
        move_encoding=encoding,
        config=MCTSConfig(
            num_simulations=args.simulations,
            add_dirichlet_noise=False,
            temperature=0.0,
        ),
    )

    result = evaluate_tactical_selector(
        positions,
        lambda board: search.select_action(search.run(board), temperature=0.0),
    )
    report = {
        "checkpoint": str(checkpoint_path),
        "checkpoint_epoch": payload.get("epoch"),
        "device": str(device),
        "simulations": args.simulations,
        "total": result.total,
        "correct": result.correct,
        "illegal": result.illegal,
        "accuracy": result.accuracy,
        "by_motif": result.by_motif,
        "by_color": result.by_color,
        "by_phase": result.by_phase,
        "failures": list(result.failures),
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"Saved benchmark report: {output_path}")


if __name__ == "__main__":
    main()
