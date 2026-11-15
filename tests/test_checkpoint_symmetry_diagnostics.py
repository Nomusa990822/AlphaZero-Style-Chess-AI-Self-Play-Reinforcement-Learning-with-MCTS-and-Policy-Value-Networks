import math

import chess
import pytest

from scripts.diagnose_checkpoint_symmetry import (
    jensen_shannon_divergence,
    mirror_move_uci,
    summarise_pairs,
)


def test_mirror_move_maps_move_to_legal_move_on_mirrored_board():
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    mirrored = board.mirror()
    mirrored_move = chess.Move.from_uci(mirror_move_uci(move.uci()))

    assert mirrored_move.uci() == "e7e5"
    assert mirrored_move in mirrored.legal_moves


def test_jensen_shannon_divergence_is_zero_for_identical_distributions():
    distribution = {"e2e4": 0.7, "d2d4": 0.3}

    assert jensen_shannon_divergence(distribution, distribution) == pytest.approx(0.0)


def test_jensen_shannon_divergence_is_bounded_by_log_two():
    left = {"e2e4": 1.0, "d2d4": 0.0}
    right = {"e2e4": 0.0, "d2d4": 1.0}

    assert jensen_shannon_divergence(left, right) == pytest.approx(math.log(2.0))


def test_mirror_summary_reports_rates_and_mean_diagnostics():
    records = [
        {
            "policy_top1_mirror_agreement": True,
            "mcts_mirror_agreement": False,
            "policy_js_divergence_nats": 0.2,
            "absolute_raw_value_difference": 0.1,
            "original_mcts_acceptable": True,
            "mirrored_mcts_acceptable": False,
        },
        {
            "policy_top1_mirror_agreement": False,
            "mcts_mirror_agreement": True,
            "policy_js_divergence_nats": 0.4,
            "absolute_raw_value_difference": 0.3,
            "original_mcts_acceptable": False,
            "mirrored_mcts_acceptable": True,
        },
    ]

    summary = summarise_pairs(records)

    assert summary["mirrored_position_pairs"] == 2
    assert summary["policy_top1_mirror_agreement_rate"] == 0.5
    assert summary["mcts_mirror_agreement_rate"] == 0.5
    assert summary["mean_policy_js_divergence_nats"] == pytest.approx(0.3)
    assert summary["mean_absolute_raw_value_difference"] == pytest.approx(0.2)
    assert summary["original_mcts_acceptable"] == 1
    assert summary["mirrored_mcts_acceptable"] == 1
