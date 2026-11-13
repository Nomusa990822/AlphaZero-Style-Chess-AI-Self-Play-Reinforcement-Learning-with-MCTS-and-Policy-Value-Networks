from pathlib import Path

import chess

from src.training.tactical_benchmark import load_tactical_positions


def test_curated_tactical_corpus_loads_and_contains_distinct_motifs():
    path = Path(__file__).parents[1] / "benchmarks" / "tactical_positions.jsonl"

    positions = load_tactical_positions(path)

    assert len(positions) >= 9
    assert {case.motif for case in positions} >= {
        "mating_net",
        "fork",
        "hanging_piece",
        "pin",
        "skewer",
    }
    sides_to_move = set()
    for case in positions:
        board = chess.Board(case.fen)
        assert board.is_valid(), f"{case.position_id} contains an invalid chess position"
        assert not board.is_game_over(claim_draw=True)
        assert all(chess.Move.from_uci(move) in board.legal_moves for move in case.acceptable_moves)
        sides_to_move.add(board.turn)

    assert sides_to_move == {chess.WHITE, chess.BLACK}
    assert sum(chess.Board(case.fen).turn == chess.WHITE for case in positions) == 5
    assert sum(chess.Board(case.fen).turn == chess.BLACK for case in positions) == 4


def test_added_skewer_and_black_tactical_positions_have_curated_legal_moves():
    path = Path(__file__).parents[1] / "benchmarks" / "tactical_positions.jsonl"
    positions = {case.position_id: case for case in load_tactical_positions(path)}

    expected = {
        "white-rook-skewers-king-and-queen-001": ("skewer", chess.WHITE, "b1a1"),
        "black-rook-skewers-king-and-queen-001": ("skewer", chess.BLACK, "b8a8"),
        "black-knight-captures-hanging-rook-001": ("hanging_piece", chess.BLACK, "c6e5"),
        "black-queen-checking-fork-rook-001": ("fork", chess.BLACK, "b8b4"),
    }
    for position_id, (motif, turn, move) in expected.items():
        case = positions[position_id]
        board = chess.Board(case.fen)
        assert case.motif == motif
        assert board.turn == turn
        assert move in case.acceptable_moves
        assert chess.Move.from_uci(move) in board.legal_moves
