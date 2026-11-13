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
    assert len(sequences) >= 2
    assert {sequence.motifs[0] for sequence in sequences} >= {
        "fork", "discovered_attack"
    }
    for sequence in sequences:
        board = chess.Board(sequence.fen)
        assert board.is_valid()
        assert len(sequence.plies) >= 3
        for ply in sequence.plies:
            assert all(chess.Move.from_uci(move) in board.legal_moves for move in ply.acceptable_moves)
            board.push(chess.Move.from_uci(sorted(ply.acceptable_moves)[0]))


def test_sequence_evaluator_scores_complete_combinations():
    sequences = load_tactical_sequences(CORPUS)
    selected = iter([
        "c6d4", "f3g4", "d4e2",
        "e4f6", "e8d8", "f6h7",
    ])
    result = evaluate_tactical_sequences(sequences, lambda board: next(selected))

    assert result.total_sequences == 2
    assert result.completed_sequences == 2
    assert result.attempted_plies == 6
    assert result.correct_plies == 6
    assert result.illegal_moves == 0
    assert result.sequence_completion_rate == 1.0
    assert result.ply_accuracy == 1.0
    assert result.by_color["white"]["correct"] == 3
    assert result.by_color["black"]["correct"] == 3
    assert result.by_phase["middlegame"]["total"] == 6


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
