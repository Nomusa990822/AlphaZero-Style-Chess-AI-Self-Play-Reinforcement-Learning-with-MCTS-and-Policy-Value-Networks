from pathlib import Path

import chess
import pytest

from src.training.tactical_benchmark import (
    evaluate_tactical_sequences,
    load_tactical_sequences,
)


CORPUS = Path(__file__).parents[1] / "benchmarks" / "tactical_sequences.jsonl"


def test_curated_combinations_replay_as_legal_multi_ply_lines():
    sequences = load_tactical_sequences(CORPUS)
    assert len(sequences) >= 11
    assert {sequence.motifs[0] for sequence in sequences} >= {
        "fork", "discovered_attack", "decoy", "removal_of_defender", "zwischenzug", "overloaded_defender", "defensive_resource"
    }
    for sequence in sequences:
        board = chess.Board(sequence.fen)
        assert board.is_valid()
        assert len(sequence.plies) >= 3
        for ply in sequence.plies:
            assert all(chess.Move.from_uci(move) in board.legal_moves for move in ply.acceptable_moves)
            board.push(chess.Move.from_uci(sorted(ply.acceptable_moves)[0]))



def test_defensive_countercheck_sequences_really_resolve_check_and_countercheck():
    sequences = load_tactical_sequences(CORPUS)
    expected = {
        "white-countercheck-interposition-001": {
            "first": "b5e2",
            "interposition_square": chess.E2,
            "king_square": chess.E1,
            "attacked_king": chess.H5,
        },
        "black-countercheck-interposition-001": {
            "first": "b4e7",
            "interposition_square": chess.E7,
            "king_square": chess.E8,
            "attacked_king": chess.H4,
        },
    }
    selected = {sequence.sequence_id: sequence for sequence in sequences}

    assert set(expected) <= set(selected)
    for sequence_id, details in expected.items():
        sequence = selected[sequence_id]
        board = chess.Board(sequence.fen)
        assert board.is_check()

        move = chess.Move.from_uci(details["first"])
        assert move in board.legal_moves
        bishop = board.piece_at(move.from_square)
        assert bishop == chess.Piece(chess.BISHOP, board.turn)
        board.push(move)

        # The interposition must end the original check and give check to the
        # opposing king; merely having a legal bishop move is not sufficient.
        assert not board.is_attacked_by(board.turn, details["king_square"])
        assert board.piece_at(details["interposition_square"]) == bishop
        assert board.is_check()
        assert board.is_attacked_by(not board.turn, details["attacked_king"])

        king_move = chess.Move.from_uci(sorted(sequence.plies[1].acceptable_moves)[0])
        assert king_move in board.legal_moves
        assert board.piece_at(details["king_square"]) == chess.Piece(chess.KING, not board.turn)

def test_sequence_evaluator_scores_complete_combinations():
    sequences = load_tactical_sequences(CORPUS)
    selected = iter([
        "c6d4", "f3g4", "d4e2",
        "e4f6", "e8d8", "f6h7",
        "e7h7", "g5h6", "h7h6", "h5h6", "f2g4",
        "e4d4", "e5d4", "e3d3", "c8c1", "g1h2",
        "c8c4", "c2c4", "d6b5",
        "d1d8", "g8f7", "e1e4",
        "d8d1", "g1f2", "e8e5",
        "f1f8", "d7f8", "e1e5",
        "f8f1", "d2f1", "e8e4",
        "b5e2", "h5g6", "e1f2",
        "b4e7", "h4g3", "e8f7",
    ])
    result = evaluate_tactical_sequences(sequences, lambda board: next(selected))

    assert result.total_sequences == 11
    assert result.completed_sequences == 11
    assert result.attempted_plies == 37
    assert result.correct_plies == 37
    assert result.illegal_moves == 0
    assert result.sequence_completion_rate == 1.0
    assert result.ply_accuracy == 1.0
    assert result.by_color["white"]["correct"] == 18
    assert result.by_color["black"]["correct"] == 19
    assert result.by_phase["middlegame"]["total"] == 37


def test_sequence_evaluator_stops_and_records_first_missed_tactical_ply():
    sequence = load_tactical_sequences(CORPUS)[0]
    selected = iter(["c6d4", "f3g4", "d4f5"])
    result = evaluate_tactical_sequences([sequence], lambda board: next(selected))

    assert result.completed_sequences == 0
    assert result.attempted_plies == 3
    assert result.correct_plies == 2
    assert result.sequence_completion_rate == 0.0
    assert result.failures == ({
        "id": sequence.sequence_id,
        "ply": 3,
        "side_to_move": "black",
        "selected": "d4f5",
        "acceptable_moves": ["d4e2"],
    },)


def test_sequence_loader_rejects_illegal_move(tmp_path):
    path = tmp_path / "invalid.jsonl"
    path.write_text(
        '{"id":"bad","motifs":["fork","pin"],"fen":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",'
        '"phase":"endgame","plies":[{"acceptable_moves":["e2e5"],"annotation":"bad"},'
        '{"acceptable_moves":["e2e3"],"annotation":"bad"}]}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="illegal moves"):
        load_tactical_sequences(path)
