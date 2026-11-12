import pytest

from src.engine.move_encoding import MoveEncoding
from src.training.evaluator import NetworkEvaluator


def test_evaluation_defaults_are_deterministic():
    evaluator = NetworkEvaluator(MoveEncoding())

    assert evaluator.mcts_config.add_dirichlet_noise is False
    assert evaluator.mcts_config.temperature == 0.0


def test_evaluation_requires_colour_balanced_game_pairs():
    evaluator = NetworkEvaluator(MoveEncoding())

    with pytest.raises(ValueError, match="even number"):
        evaluator.compare_models(None, None, num_games=3)


def test_confidence_bound_rejects_marginal_small_sample_result():
    from src.training.evaluator import EvaluationResult

    marginal = EvaluationResult(wins=13, losses=11, draws=0, games_played=24)
    strong = EvaluationResult(wins=18, losses=6, draws=0, games_played=24)

    assert marginal.score >= 0.50
    assert marginal.lower_confidence_bound < 0.50
    assert strong.lower_confidence_bound > 0.50
