from pathlib import Path

import chess

from src.training.tactical_benchmark import load_tactical_positions


def test_curated_tactical_corpus_loads_and_contains_distinct_motifs():
    path = Path(__file__).parents[1] / "benchmarks" / "tactical_positions.jsonl"

    positions = load_tactical_positions(path)

    assert len(positions) >= 22
    assert {case.motif for case in positions} >= {
        "mating_net",
        "fork",
        "hanging_piece",
        "pin",
        "skewer",
        "discovered_attack",
        "defensive_resource",
        "endgame_tactic",
        "double_attack",
        "deflection",
        "decoy",
        "removal_of_defender",
        "interference",
        "overloaded_defender",
        "trapped_piece",
    }
    sides_to_move = set()
    for case in positions:
        board = chess.Board(case.fen)
        assert board.is_valid(), f"{case.position_id} contains an invalid chess position"
        assert not board.is_game_over(claim_draw=True)
        assert all(chess.Move.from_uci(move) in board.legal_moves for move in case.acceptable_moves)
        sides_to_move.add(board.turn)

    assert sides_to_move == {chess.WHITE, chess.BLACK}
    assert sum(chess.Board(case.fen).turn == chess.WHITE for case in positions) == 14
    assert sum(chess.Board(case.fen).turn == chess.BLACK for case in positions) == 12


def test_added_skewers_and_black_tactical_positions_have_curated_legal_moves():
    path = Path(__file__).parents[1] / "benchmarks" / "tactical_positions.jsonl"
    positions = {case.position_id: case for case in load_tactical_positions(path)}

    expected = {
        "white-rook-skewers-king-and-queen-001": ("skewer", chess.WHITE, "b1a1"),
        "black-rook-skewers-king-and-queen-001": ("skewer", chess.BLACK, "b8a8"),
        "black-knight-captures-hanging-rook-001": ("hanging_piece", chess.BLACK, "c6e5"),
        "black-rook-captures-absolutely-pinned-rook-001": ("pin", chess.BLACK, "e8e2"),
    }
    for position_id, (motif, turn, move) in expected.items():
        case = positions[position_id]
        board = chess.Board(case.fen)
        assert case.motif == motif
        assert board.turn == turn
        assert move in case.acceptable_moves
        assert chess.Move.from_uci(move) in board.legal_moves


def test_discovered_attack_defensive_resource_and_endgame_examples():
    path = Path(__file__).parents[1] / "benchmarks" / "tactical_positions.jsonl"
    positions = {case.position_id: case for case in load_tactical_positions(path)}

    expected = {
        "white-knight-discovered-check-queen-attack-001": (
            "discovered_attack", chess.WHITE, "e4f6", "middlegame"
        ),
        "black-knight-captures-checking-rook-001": (
            "defensive_resource", chess.BLACK, "c2e1", "middlegame"
        ),
        "white-pawn-promotes-with-check-001": (
            "endgame_tactic", chess.WHITE, "a7a8q", "endgame"
        ),
        "black-pawn-promotes-with-check-001": (
            "endgame_tactic", chess.BLACK, "a2a1q", "endgame"
        ),
    }
    for position_id, (motif, turn, move, phase) in expected.items():
        case = positions[position_id]
        board = chess.Board(case.fen)
        assert case.motif == motif
        assert board.turn == turn
        assert case.phase == phase
        assert move in case.acceptable_moves
        assert chess.Move.from_uci(move) in board.legal_moves
