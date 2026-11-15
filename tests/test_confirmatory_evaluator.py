import pytest

from src.training.confirmatory_evaluator import (
    PAIR_COUNT,
    T_ONE_SIDED_90_DF23,
    load_confirmatory_openings,
    paired_student_t_lcb90,
)


def test_confirmatory_suite_has_24_distinct_positions_and_eight_families():
    openings = load_confirmatory_openings()
    assert len(openings) == PAIR_COUNT
    assert len({opening_id for opening_id, _ in openings}) == PAIR_COUNT
    assert len({board.fen(en_passant="fen") for _, board in openings}) == PAIR_COUNT
    assert all(board.is_valid() and not board.is_game_over(claim_draw=True) for _, board in openings)


def test_student_t_critical_value_is_one_sided_90_percent_df23():
    assert T_ONE_SIDED_90_DF23 == pytest.approx(1.319460, abs=1e-6)


def test_paired_lcb_uses_24_pair_observations():
    scores = [1.0] * 18 + [0.0] * 6
    assert paired_student_t_lcb90(scores) == pytest.approx(
        0.75 - T_ONE_SIDED_90_DF23 * (0.4522670169 / 4.898979486), abs=1e-6
    )


def test_paired_lcb_requires_exactly_24_scores():
    with pytest.raises(ValueError, match="exactly 24"):
        paired_student_t_lcb90([0.5] * 23)


def test_paired_lcb_rejects_invalid_scores():
    with pytest.raises(ValueError, match="finite values"):
        paired_student_t_lcb90([0.5] * 23 + [float("nan")])
