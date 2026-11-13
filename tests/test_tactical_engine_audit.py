import chess
import chess.engine

from scripts.audit_tactical_corpus import audit_position
from src.training.tactical_benchmark import TacticalPosition


class FakeEngine:
    def analyse(self, board, limit, *, multipv=None, root_moves=None):
        if root_moves:
            move = root_moves[0]
            score = 25 if move.uci() == "e2e4" else -40
            return {
                "score": chess.engine.PovScore(chess.engine.Cp(score), board.turn),
                "pv": [move],
            }
        moves = list(board.legal_moves)
        best = chess.Move.from_uci("e2e4")
        second = next(move for move in moves if move != best)
        return [
            {
                "score": chess.engine.PovScore(chess.engine.Cp(25), board.turn),
                "pv": [best],
            },
            {
                "score": chess.engine.PovScore(chess.engine.Cp(10), board.turn),
                "pv": [second],
            },
        ]


def test_audit_position_compares_accepted_moves_with_engine_best():
    case = TacticalPosition(
        position_id="opening-e4-test",
        motif="endgame_tactic",
        fen=chess.STARTING_FEN,
        acceptable_moves=frozenset({"e2e4"}),
        annotation="Test annotation.",
        phase="opening",
    )

    result = audit_position(
        FakeEngine(),
        case,
        depth=8,
        multipv=2,
        max_loss_cp=150,
    )

    assert result["engine_best_score_cp"] == 25
    assert result["engine_top_lines"][0]["move"] == "e2e4"
    assert result["accepted_move_analysis"][0]["move"] == "e2e4"
    assert result["accepted_move_analysis"][0]["loss_from_engine_best_cp"] == 0
    assert result["review_status"] == "engine_supports_at_least_one_accepted_move"


def test_audit_position_flags_accepted_move_outside_tolerance():
    case = TacticalPosition(
        position_id="opening-e4-test",
        motif="endgame_tactic",
        fen=chess.STARTING_FEN,
        acceptable_moves=frozenset({"d2d4"}),
        annotation="Test annotation.",
        phase="opening",
    )

    result = audit_position(
        FakeEngine(),
        case,
        depth=8,
        multipv=2,
        max_loss_cp=20,
    )

    assert result["accepted_move_analysis"][0]["loss_from_engine_best_cp"] == 65
    assert result["accepted_move_within_tolerance"] == []
    assert result["review_status"] == "human_review_required_engine_disagrees"
