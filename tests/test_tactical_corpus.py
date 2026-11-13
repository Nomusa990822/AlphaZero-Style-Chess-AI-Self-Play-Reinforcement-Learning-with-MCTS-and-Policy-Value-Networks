from pathlib import Path

import chess

from src.training.tactical_benchmark import load_tactical_positions


def test_curated_tactical_corpus_loads_and_contains_distinct_motifs():
    path = Path(__file__).parents[1] / "benchmarks" / "tactical_positions.jsonl"

    positions = load_tactical_positions(path)

    assert len(positions) >= 4
    assert {case.motif for case in positions} >= {
        "mating_net",
        "fork",
        "hanging_piece",
    }
    sides_to_move = set()
    for case in positions:
        board = chess.Board(case.fen)
        assert board.is_valid(), f"{case.position_id} contains an invalid chess position"
        assert not board.is_game_over(claim_draw=True)
        assert all(chess.Move.from_uci(move) in board.legal_moves for move in case.acceptable_moves)
        sides_to_move.add(board.turn)

    assert sides_to_move == {chess.WHITE, chess.BLACK}
