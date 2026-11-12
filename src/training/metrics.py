"""
Training metrics utilities for logging AlphaZero-style experiments.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class IterationMetrics:
    """
    Stores one outer training iteration summary.
    """
    iteration: int
    self_play_games: int
    replay_buffer_size: int
    total_positions_generated: int
    average_game_length: float
    average_game_result_white_score: float
    training_epochs: int
    final_total_loss: float
    final_policy_loss: float
    final_value_loss: float
    evaluation_games: int
    evaluation_wins: int
    evaluation_losses: int
    evaluation_draws: int
    evaluation_score: float
    model_promoted: bool


class MetricsLogger:
    """
    Append iteration metrics to a JSONL file and optionally save full summaries.
    """

    def __init__(self, log_dir: str | Path = "data/logs") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def append_iteration_metrics(
        self,
        metrics: IterationMetrics,
        filename: str = "training_metrics.jsonl",
    ) -> None:
        """
        Append one iteration record as JSON line.
        """
        path = self.log_dir / filename
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(metrics)) + "\n")

    def append_self_play_game(
        self,
        iteration: int,
        game_number: int,
        result: str,
        moves: list[str],
        samples: int,
        elapsed_seconds: float,
        ended_by_resignation: bool = False,
        ended_by_adjudication: bool = False,
        filename: str = "self_play_games.jsonl",
    ) -> None:
        """Persist a complete game record as soon as self-play finishes."""
        path = self.log_dir / filename
        record = {
            "iteration": iteration,
            "game": game_number,
            "result": result,
            "move_count": len(moves),
            "moves_uci": moves,
            "samples": samples,
            "elapsed_seconds": round(elapsed_seconds, 3),
            "ended_by_resignation": ended_by_resignation,
            "ended_by_adjudication": ended_by_adjudication,
        }
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\\n")

    def save_json_summary(
        self,
        payload: dict[str, Any],
        filename: str,
    ) -> None:
        """
        Save a full JSON summary.
        """
        path = self.log_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
