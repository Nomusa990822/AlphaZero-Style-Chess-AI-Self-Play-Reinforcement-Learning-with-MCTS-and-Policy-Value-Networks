import json
from pathlib import Path

from src.training.metrics import IterationMetrics, MetricsLogger


def test_metrics_logger_writes_files(tmp_path: Path):
    logger = MetricsLogger(log_dir=tmp_path)

    metrics = IterationMetrics(
        iteration=1,
        self_play_games=2,
        replay_buffer_size=100,
        total_positions_generated=80,
        average_game_length=40.0,
        average_game_result_white_score=0.5,
        training_epochs=2,
        final_total_loss=1.2,
        final_policy_loss=0.8,
        final_value_loss=0.4,
        evaluation_games=4,
        evaluation_wins=2,
        evaluation_losses=1,
        evaluation_draws=1,
        evaluation_score=0.625,
        model_promoted=True,
    )

    logger.append_iteration_metrics(metrics)
    logger.save_json_summary({"ok": True}, "summary.json")

    metrics_file = tmp_path / "training_metrics.jsonl"
    summary_file = tmp_path / "summary.json"

    assert metrics_file.exists()
    assert summary_file.exists()

    lines = metrics_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1

    payload = json.loads(lines[0])
    assert payload["iteration"] == 1
