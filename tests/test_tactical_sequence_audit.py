import chess
import chess.engine

from scripts.audit_tactical_corpus import audit_sequence
from src.training.tactical_benchmark import (
    TacticalSequence,
    TacticalSequencePly,
)


class SequenceFakeEngine:
    def analyse(self, board, limit, *, multipv=None, root_moves=None):
        move = root_moves[0] if root_moves else next(iter(board.legal_moves))
        return {
            "score": chess.engine.PovScore(chess.engine.Cp(30), board.turn),
            "pv": [move],
        }


def test_audit_sequence_reviews_every_ply_on_the_annotated_line():
    sequence = TacticalSequence(
        sequence_id="opening-line-audit",
        motifs=("fork", "hanging_piece"),
        fen=chess.STARTING_FEN,
        plies=(
            TacticalSequencePly(frozenset({"e2e4"}), "White opens the centre."),
            TacticalSequencePly(frozenset({"e7e5"}), "Black replies symmetrically."),
            TacticalSequencePly(frozenset({"g1f3"}), "White develops with a threat."),
        ),
        phase="opening",
    )

    result = audit_sequence(
        SequenceFakeEngine(),
        sequence,
        depth=8,
        multipv=2,
        max_loss_cp=50,
    )

    assert result["plies"] == 3
    assert result["supported_plies"] == 3
    assert result["flagged_plies_for_human_review"] == 0
    assert result["review_status"] == "engine_supports_all_annotated_plies"
    assert [ply["human_acceptable_moves"] for ply in result["line_review"]] == [
        ["e2e4"], ["e7e5"], ["g1f3"]
    ]
