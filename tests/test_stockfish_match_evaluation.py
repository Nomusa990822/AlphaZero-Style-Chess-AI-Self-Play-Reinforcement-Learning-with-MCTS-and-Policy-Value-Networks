import pytest

from evaluate_vs_stockfish import (
    DEFAULT_ELO_LEVELS,
    OPENING_LINES,
    build_match_schedule,
    build_opening_board,
    summarise,
)


def test_fixed_opening_lines_are_legal_and_leave_white_to_move():
    for line in OPENING_LINES:
        board = build_opening_board(line)
        assert board.turn
        assert not board.is_game_over()


def test_schedule_pairs_each_opening_with_both_model_colours():
    schedule = build_match_schedule(12)
    assert len(schedule) == 12
    for index in range(len(OPENING_LINES)):
        pair = [item for item in schedule if item["opening_index"] == index]
        assert {item["model_color"] for item in pair} == {"white", "black"}


def test_schedule_repeats_are_deterministic_and_balanced():
    schedule = build_match_schedule(24)
    assert len(schedule) == 24
    assert sum(item["model_color"] == "white" for item in schedule) == 12
    assert sum(item["model_color"] == "black" for item in schedule) == 12


def test_match_summary_counts_results_and_colours():
    games = [
        {"model_color": "white", "model_result": "win", "plies": 40},
        {"model_color": "black", "model_result": "draw", "plies": 80},
        {"model_color": "white", "model_result": "loss", "plies": 60},
    ]
    result = summarise(games)
    assert (result["wins"], result["draws"], result["losses"]) == (1, 1, 1)
    assert result["score"] == pytest.approx(0.5)
    assert result["white"]["games"] == 2
    assert result["black"]["draws"] == 1


def test_default_stockfish_levels_span_weak_to_intermediate():
    assert DEFAULT_ELO_LEVELS == (1320, 1600, 1900)
