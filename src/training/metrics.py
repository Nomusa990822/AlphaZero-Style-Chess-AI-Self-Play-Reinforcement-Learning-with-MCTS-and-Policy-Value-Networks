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
