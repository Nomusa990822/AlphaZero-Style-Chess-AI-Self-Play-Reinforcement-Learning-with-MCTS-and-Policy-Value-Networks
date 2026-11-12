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
