import pytest

from src.engine.move_encoding import MoveEncoding
from src.training.evaluator import (
    MIN_PROMOTION_GAMES,
    EvaluationResult,
    NetworkEvaluator,
)


def test_evaluation_defaults_are_deterministic():
    evaluator = NetworkEvaluator(MoveEncoding())

    assert evaluator.mcts_config.add_dirichlet_noise is False
    assert evaluator.mcts_config.temperature == 0.0


def test_evaluation_requires_colour_balanced_game_pairs():
    evaluator = NetworkEvaluator(MoveEncoding())

    with pytest.raises(ValueError, match="even number"):
        evaluator.compare_models(None, None, num_games=3)


def test_confidence_bound_rejects_marginal_small_sample_result():
    marginal = EvaluationResult(wins=13, losses=11, draws=0, games_played=24)
    strong = EvaluationResult(wins=18, losses=6, draws=0, games_played=24)

    assert marginal.score > 0.50
    assert marginal.lower_confidence_bound < 0.50
    assert strong.lower_confidence_bound > 0.50


def test_promotion_requires_candidate_to_beat_current_champion(monkeypatch):
    evaluator = NetworkEvaluator(MoveEncoding())
    candidate_win = EvaluationResult(wins=18, losses=6, draws=0, games_played=24)
    monkeypatch.setattr(evaluator, "compare_models", lambda *args, **kwargs: candidate_win)

    promoted, result = evaluator.should_promote_candidate(None, None, num_games=24)

    assert promoted is True
    assert result is candidate_win
    assert evaluator.promotion_rejection_reasons(result) == []


def test_score_above_half_is_not_enough_without_confidence(monkeypatch):
    evaluator = NetworkEvaluator(MoveEncoding())
    marginal = EvaluationResult(wins=14, losses=10, draws=0, games_played=24)
    monkeypatch.setattr(evaluator, "compare_models", lambda *args, **kwargs: marginal)

    promoted, _ = evaluator.should_promote_candidate(None, None, num_games=24)

    assert marginal.score > 0.50
    assert marginal.lower_confidence_bound <= 0.50
    assert promoted is False
    assert any("confidence bound" in reason for reason in evaluator.promotion_rejection_reasons(marginal))


def test_equal_or_lower_score_never_replaces_incumbent(monkeypatch):
    evaluator = NetworkEvaluator(MoveEncoding())
    tied = EvaluationResult(wins=0, losses=0, draws=24, games_played=24)
    monkeypatch.setattr(evaluator, "compare_models", lambda *args, **kwargs: tied)

    promoted, _ = evaluator.should_promote_candidate(None, None, num_games=24)

    assert tied.score == 0.50
    assert promoted is False
    assert any("did not exceed" in reason for reason in evaluator.promotion_rejection_reasons(tied))


def test_insufficient_game_count_never_promotes_even_a_perfect_candidate(monkeypatch):
    evaluator = NetworkEvaluator(MoveEncoding())
    small_sample = EvaluationResult(wins=22, losses=0, draws=0, games_played=22)
    monkeypatch.setattr(evaluator, "compare_models", lambda *args, **kwargs: small_sample)

    promoted, _ = evaluator.should_promote_candidate(None, None, num_games=22)

    assert small_sample.games_played < MIN_PROMOTION_GAMES
    assert small_sample.score == 1.0
    assert promoted is False
    assert any("at least 24" in reason for reason in evaluator.promotion_rejection_reasons(small_sample))


def test_promotion_requires_at_least_24_games_for_pilot_safety():
    assert MIN_PROMOTION_GAMES == 24
