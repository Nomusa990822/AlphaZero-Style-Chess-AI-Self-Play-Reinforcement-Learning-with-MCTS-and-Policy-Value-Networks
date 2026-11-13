from pathlib import Path

import chess

from src.training.tactical_benchmark import load_tactical_positions


def test_curated_tactical_corpus_loads_and_contains_distinct_motifs():
    path = Path(__file__).parents[1] / "benchmarks" / "tactical_positions.jsonl"

    positions = load_tactical_positions(path)

    assert len(positions) >= 32
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
    assert sum(chess.Board(case.fen).turn == chess.WHITE for case in positions) == 17
    assert sum(chess.Board(case.fen).turn == chess.BLACK for case in positions) == 15


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


def test_trapped_corner_bishops_are_annotated_for_both_colours():
    path = Path(__file__).parents[1] / "benchmarks" / "tactical_positions.jsonl"
    positions = {case.position_id: case for case in load_tactical_positions(path)}

    expected = {
        "white-knight-wins-trapped-corner-bishop-001": (chess.WHITE, "f7h8"),
        "black-knight-wins-trapped-corner-bishop-001": (chess.BLACK, "f2h1"),
    }
    for position_id, (turn, move) in expected.items():
        case = positions[position_id]
        board = chess.Board(case.fen)
        assert case.motif == "trapped_piece"
        assert board.turn == turn
        assert move in case.acceptable_moves
        assert chess.Move.from_uci(move) in board.legal_moves


def test_defensive_interpositions_and_checker_captures_cover_both_colours():
    path = Path(__file__).parents[1] / "benchmarks" / "tactical_positions.jsonl"
    positions = {case.position_id: case for case in load_tactical_positions(path)}

    expected = {
        "white-bishop-interposes-against-rook-check-001": (chess.WHITE, "d3e2"),
        "black-bishop-interposes-against-rook-check-001": (chess.BLACK, "d6e7"),
        "white-bishop-captures-checking-rook-001": (chess.WHITE, "c6e8"),
        "black-bishop-captures-checking-rook-001": (chess.BLACK, "c3e1"),
    }
    for position_id, (turn, move) in expected.items():
        case = positions[position_id]
        board = chess.Board(case.fen)
        assert case.motif == "defensive_resource"
        assert board.is_check()
        assert board.turn == turn
        assert move in case.acceptable_moves
        assert chess.Move.from_uci(move) in board.legal_moves

def test_counterchecking_interpositions_and_attacker_removal_cover_both_colours():
    path = Path(__file__).parents[1] / "benchmarks" / "tactical_positions.jsonl"
    positions = {case.position_id: case for case in load_tactical_positions(path)}

    counterchecks = {
        "white-bishop-counterchecks-while-interposing-001": (chess.WHITE, "b5e2"),
        "black-bishop-counterchecks-while-interposing-001": (chess.BLACK, "b4e7"),
    }
    for position_id, (turn, uci) in counterchecks.items():
        case = positions[position_id]
        board = chess.Board(case.fen)
        move = chess.Move.from_uci(uci)
        assert case.motif == "defensive_resource"
        assert board.turn == turn
        assert board.is_check()
        assert move in board.legal_moves
        board.push(move)
        assert board.is_check()  # The opponent is now in check.

    attacker_removals = {
        "white-knight-removes-bishop-attacking-queen-001": (chess.WHITE, "c4e5", chess.D4, chess.E5),
        "black-knight-removes-bishop-attacking-queen-001": (chess.BLACK, "f6e4", chess.D5, chess.E4),
    }
    for position_id, (turn, uci, queen_square, bishop_square) in attacker_removals.items():
        case = positions[position_id]
        board = chess.Board(case.fen)
        move = chess.Move.from_uci(uci)
        attacker_color = not turn
        assert case.motif == "defensive_resource"
        assert board.turn == turn
        assert queen_square in board.attacks(bishop_square)
        assert move in board.legal_moves
        board.push(move)
        assert board.piece_at(bishop_square) == chess.Piece(chess.KNIGHT, turn)
        assert board.piece_at(queen_square) == chess.Piece(chess.QUEEN, turn)
        assert not board.is_attacked_by(attacker_color, queen_square)
