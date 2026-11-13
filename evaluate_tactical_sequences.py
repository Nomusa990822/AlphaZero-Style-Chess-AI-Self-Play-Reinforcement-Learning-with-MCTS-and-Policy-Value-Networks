"""Evaluate a trained checkpoint on multi-ply tactical combinations."""

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
from src.training.tactical_benchmark import evaluate_tactical_sequences, load_tactical_sequences
from evaluate_tactics import resolve_device


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--positions", default="benchmarks/tactical_sequences.jsonl")
    parser.add_argument("--simulations", type=int, default=100)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.simulations < 1:
        parser.error("--simulations must be at least 1")

    checkpoint_path = Path(args.checkpoint)
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    sequences = load_tactical_sequences(args.positions)
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
            use_tactical_root_filter=True,
        ),
    )
    result = evaluate_tactical_sequences(
        sequences,
        lambda board: search.select_action(search.run(board), temperature=0.0),
    )
    report = {
        "checkpoint": str(checkpoint_path),
        "checkpoint_epoch": payload.get("epoch"),
        "device": str(device),
        "simulations": args.simulations,
        "evaluation_type": "annotated_principal_variation_line_following",
        "total_sequences": result.total_sequences,
        "completed_sequences": result.completed_sequences,
        "attempted_plies": result.attempted_plies,
        "correct_plies": result.correct_plies,
        "illegal_moves": result.illegal_moves,
        "sequence_completion_rate": result.sequence_completion_rate,
        "ply_accuracy": result.ply_accuracy,
        "by_combination": result.by_combination,
        "by_color": result.by_color,
        "by_phase": result.by_phase,
        "failures": list(result.failures),
        "limitations": [
            "This measures agreement with an annotated principal variation, not proof that the line is forced.",
            "The opponent's moves follow the curated line; alternative defences are not exhaustively searched by this metric.",
            "A trained checkpoint is required; an untrained or random model score is not playing-strength evidence.",
        ],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Saved sequence benchmark report: {output}")


if __name__ == "__main__":
    main()
