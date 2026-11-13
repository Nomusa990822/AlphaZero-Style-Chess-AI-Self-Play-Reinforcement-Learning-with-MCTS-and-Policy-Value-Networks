#!/usr/bin/env python3
"""Measure the CPU cost of SEE-guided MCTS root expansion without a checkpoint."""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import statistics
import time
from pathlib import Path

import chess
import numpy as np

from src.engine.move_encoding import MoveEncoding
from src.mcts.node import MCTSNode
from src.mcts.search import MCTS, MCTSConfig


POSITIONS = {
    "starting_position": chess.STARTING_FEN,
    "simple_capture": "4k3/8/8/3p4/4P3/8/8/4K3 w - - 0 1",
    "poisoned_queen_capture": "4k3/8/2p5/3q4/4P3/8/8/4K3 w - - 0 1",
    "promotion_choices": "4k3/P7/8/8/8/8/8/4K3 w - - 0 1",
}


class UniformInference:
    """Deterministic stand-in; deliberately excludes neural inference time."""

    def __init__(self, action_size: int) -> None:
        self.action_size = action_size

    def predict(self, board: chess.Board) -> tuple[np.ndarray, float]:
        return np.ones(self.action_size, dtype=np.float32), 0.0


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


def measure_expansion(
    fen: str,
    encoding: MoveEncoding,
    inference: UniformInference,
    use_see: bool,
) -> float:
    board = chess.Board(fen)
    original_fen = board.fen()
    search = MCTS(
        inference=inference,
        move_encoding=encoding,
        config=MCTSConfig(
            num_simulations=0,
            add_dirichlet_noise=False,
            use_tactical_root_filter=False,
            use_static_exchange_ordering=use_see,
        ),
    )
    root = MCTSNode(board=board.copy(stack=True))
    started = time.perf_counter_ns()
    search._evaluate_and_expand(root, is_root=True)
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000

    if len(root.children) != board.legal_moves.count():
        raise RuntimeError("Root expansion did not preserve every legal move")
    if not math.isclose(sum(child.prior for child in root.children.values()), 1.0, abs_tol=1e-6):
        raise RuntimeError("Root priors are not normalized")
    if board.fen() != original_fen:
        raise RuntimeError("Benchmark mutated its input board")
    return elapsed_ms


def run_benchmark(repeats: int = 15, warmups: int = 3) -> dict:
    if repeats < 3:
        raise ValueError("repeats must be at least 3 for a useful timing sample")
    if warmups < 0:
        raise ValueError("warmups cannot be negative")

    encoding = MoveEncoding()
    inference = UniformInference(encoding.action_size)
    results = []
    all_off: list[float] = []
    all_on: list[float] = []

    for name, fen in POSITIONS.items():
        board = chess.Board(fen)
        if not board.is_valid() or board.is_game_over(claim_draw=True):
            raise RuntimeError(f"Invalid or terminal benchmark position: {name}")
        tactical_moves = [
            move for move in board.legal_moves
            if board.is_capture(move) or move.promotion is not None
        ]

        for _ in range(warmups):
            measure_expansion(fen, encoding, inference, False)
            measure_expansion(fen, encoding, inference, True)

        off_samples: list[float] = []
        on_samples: list[float] = []
        for index in range(repeats):
            if index % 2 == 0:
                off_samples.append(measure_expansion(fen, encoding, inference, False))
                on_samples.append(measure_expansion(fen, encoding, inference, True))
            else:
                on_samples.append(measure_expansion(fen, encoding, inference, True))
                off_samples.append(measure_expansion(fen, encoding, inference, False))

        off_median = statistics.median(off_samples)
        on_median = statistics.median(on_samples)
        overhead_pct = ((on_median / off_median) - 1.0) * 100.0 if off_median else None
        all_off.extend(off_samples)
        all_on.extend(on_samples)
        results.append({
            "position": name,
            "legal_moves": board.legal_moves.count(),
            "capture_or_promotion_candidates": len(tactical_moves),
            "see_disabled_median_ms": round(off_median, 6),
            "see_enabled_median_ms": round(on_median, 6),
            "see_disabled_p95_ms": round(percentile(off_samples, 0.95), 6),
            "see_enabled_p95_ms": round(percentile(on_samples, 0.95), 6),
            "median_overhead_percent": round(overhead_pct, 2) if overhead_pct is not None else None,
        })

    off_median = statistics.median(all_off)
    on_median = statistics.median(all_on)
    return {
        "benchmark": "SEE-guided MCTS root expansion CPU overhead",
        "measurement_scope": (
            "Root policy conversion, optional SEE prior adjustment and child expansion; "
            "neural inference, MCTS simulations, tactical root filters and trained checkpoints excluded."
        ),
        "code_revision": os.environ.get("GITHUB_SHA", "local-uncommitted"),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "repeats_per_position": repeats,
        "warmups_per_mode_per_position": warmups,
        "positions": results,
        "aggregate": {
            "paired_samples": len(all_off),
            "see_disabled_median_ms": round(off_median, 6),
            "see_enabled_median_ms": round(on_median, 6),
            "median_overhead_percent": round(((on_median / off_median) - 1.0) * 100.0, 2) if off_median else None,
            "see_disabled_p95_ms": round(percentile(all_off, 0.95), 6),
            "see_enabled_p95_ms": round(percentile(all_on, 0.95), 6),
        },
        "interpretation_limit": (
            "Microbenchmark only. Results are specific to this runner and synthetic uniform inference; "
            "they are not end-to-end search speed, playing-strength or Elo measurements."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=15)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--output", type=Path, default=Path("reports/see-root-overhead-benchmark.json"))
    args = parser.parse_args()

    report = run_benchmark(repeats=args.repeats, warmups=args.warmups)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
