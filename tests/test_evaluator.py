import chess
import pytest
from src.engine.move_encoding import MoveEncoding
from src.training.evaluator import MIN_OPENING_PAIRS, MIN_PROMOTION_GAMES, EvaluationResult, NetworkEvaluator, load_evaluation_openings
from src.training.pipeline import PipelineConfig


def test_evaluation_defaults_are_deterministic():
    evaluator = NetworkEvaluator(MoveEncoding())
    assert evaluator.mcts_config.add_dirichlet_noise is False
    assert evaluator.mcts_config.temperature == 0.0


def test_opening_suite_has_twelve_distinct_valid_positions():
    openings = load_evaluation_openings()
    assert len(openings) == MIN_OPENING_PAIRS
    assert len({opening_id for opening_id, _ in openings}) == MIN_OPENING_PAIRS
    assert len({board.fen() for _, board in openings}) == MIN_OPENING_PAIRS
    assert all(board.is_valid() and not board.is_game_over(claim_draw=True) for _, board in openings)


def test_evaluation_requires_colour_balanced_game_pairs():
    evaluator = NetworkEvaluator(MoveEncoding())
    with pytest.raises(ValueError, match="even number"):
        evaluator.compare_models(None, None, num_games=3)


def test_evaluation_rejects_more_games_than_distinct_opening_suite():
    evaluator = NetworkEvaluator(MoveEncoding())
    with pytest.raises(ValueError, match="distinct opening pairs"):
        evaluator.compare_models(None, None, num_games=26)


def test_compare_models_uses_each_opening_in_both_colours(monkeypatch):
    evaluator = NetworkEvaluator(MoveEncoding())
    candidate, incumbent = object(), object()
    seen = []

    def fake_game(agent_white, agent_black, max_moves=200, starting_board=None):
        candidate_is_white = agent_white.inference is candidate
        seen.append((starting_board.fen(), candidate_is_white))
        return "1-0" if candidate_is_white else "0-1"

    monkeypatch.setattr(evaluator, "_play_single_game", fake_game)
    result = evaluator.compare_models(candidate, incumbent, num_games=24)

    assert len(seen) == 24
    assert len({fen for fen, _ in seen}) == 24
    assert sum(is_white for _, is_white in seen) == 12
    assert sum(not is_white for _, is_white in seen) == 12
    assert result.wins == 24 and result.losses == result.draws == 0
    assert result.candidate_white_wins == result.candidate_black_wins == 12
    assert result.opening_pair_scores == (1.0,) * 12
    assert len(result.opening_ids) == 12
    assert len(result.opening_pair_results) == 12
    assert all(item["candidate_as_white"] == "win" and item["candidate_as_black"] == "win" for item in result.opening_pair_results)


def test_confidence_bound_uses_independent_opening_pair_scores():
    result = EvaluationResult(wins=18, losses=6, draws=0, games_played=24, opening_pair_scores=(1.0,) * 9 + (0.0,) * 3)
    assert result.score == 0.75
    assert result.lower_confidence_bound > 0.50


def test_confidence_bound_rejects_marginal_small_sample_result():
    marginal = EvaluationResult(wins=14, losses=10, draws=0, games_played=24)
    strong = EvaluationResult(wins=18, losses=6, draws=0, games_played=24)
    assert marginal.score > 0.50
    assert marginal.lower_confidence_bound < 0.50
    assert strong.lower_confidence_bound > 0.50


def test_promotion_requires_candidate_to_beat_current_champion(monkeypatch):
    evaluator = NetworkEvaluator(MoveEncoding())
    candidate_win = EvaluationResult(
        wins=18, losses=6, draws=0, games_played=24,
        opening_pair_scores=(1.0,) * 9 + (0.0,) * 3,
        opening_ids=tuple(f"opening-{i}" for i in range(12)),
    )
    monkeypatch.setattr(evaluator, "compare_models", lambda *args, **kwargs: candidate_win)
    promoted, result = evaluator.should_promote_candidate(None, None, num_games=24)
    assert promoted is True
    assert result is candidate_win
    assert evaluator.promotion_rejection_reasons(result) == []


def test_score_above_half_is_not_enough_without_confidence(monkeypatch):
    evaluator = NetworkEvaluator(MoveEncoding())
    marginal = EvaluationResult(
        wins=14, losses=10, draws=0, games_played=24,
        opening_pair_scores=(1.0,) * 7 + (0.0,) * 5,
        opening_ids=tuple(f"opening-{i}" for i in range(12)),
    )
    monkeypatch.setattr(evaluator, "compare_models", lambda *args, **kwargs: marginal)
    promoted, _ = evaluator.should_promote_candidate(None, None, num_games=24)
    assert marginal.score > 0.50
    assert marginal.lower_confidence_bound <= 0.50
    assert promoted is False
    assert any("confidence bound" in reason for reason in evaluator.promotion_rejection_reasons(marginal))


def test_equal_or_lower_score_never_replaces_incumbent(monkeypatch):
    evaluator = NetworkEvaluator(MoveEncoding())
    tied = EvaluationResult(
        wins=0, losses=0, draws=24, games_played=24,
        opening_pair_scores=(0.5,) * 12,
        opening_ids=tuple(f"opening-{i}" for i in range(12)),
    )
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
    assert any("distinct opening pairs" in reason for reason in evaluator.promotion_rejection_reasons(small_sample))


def test_pipeline_default_gating_games_meets_promotion_sample_minimum():
    assert PipelineConfig().gating_games == MIN_PROMOTION_GAMES


def test_pipeline_rejects_unbalanced_gating_configuration():
    with pytest.raises(ValueError, match="even number"):
        PipelineConfig(gating_games=3)


def test_illegal_evaluator_move_aborts_the_match():
    evaluator = NetworkEvaluator(MoveEncoding())
    class IllegalMoveAgent:
        def choose_move(self, board, temperature=0.0):
            return chess.Move.from_uci("a1a8")
    with pytest.raises(RuntimeError, match="illegal move"):
        evaluator._play_single_game(IllegalMoveAgent(), IllegalMoveAgent())



def test_pipeline_rejects_more_games_than_opening_suite():
    with pytest.raises(ValueError, match="cannot exceed 24"):
        PipelineConfig(gating_games=26)
