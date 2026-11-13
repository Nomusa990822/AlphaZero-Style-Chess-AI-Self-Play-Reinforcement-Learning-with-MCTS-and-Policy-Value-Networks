from pathlib import Path

import chess

from src.training.tactical_benchmark import load_tactical_positions


CORPUS_PATH = Path(__file__).parents[1] / "benchmarks" / "tactical_positions.jsonl"


def cases_by_id():
    return {case.position_id: case for case in load_tactical_positions(CORPUS_PATH)}


def play_annotated_move(position_id):
    case = cases_by_id()[position_id]
    board = chess.Board(case.fen)
    move = chess.Move.from_uci(next(iter(case.acceptable_moves)))
    mover = board.turn
    board.push(move)
    return board, move, mover


def test_mating_net_move_is_checkmate():
    board, _, _ = play_annotated_move("mate-in-one-queen-mate-001")
    assert board.is_checkmate()


def test_both_fork_moves_attack_the_king_and_queen():
    cases = cases_by_id()
    expected = {
        "knight-fork-king-queen-001": ("c5d7", chess.BLACK, chess.E8, chess.F6),
        "black-knight-checking-fork-king-queen-001": ("c6d4", chess.WHITE, chess.F3, chess.E2),
    }
    for position_id, (uci, victim_color, king_square, queen_square) in expected.items():
        case = cases[position_id]
        board = chess.Board(case.fen)
        mover = board.turn
        move = chess.Move.from_uci(uci)
        board.push(move)
        assert board.is_attacked_by(mover, king_square)
        assert board.is_attacked_by(mover, queen_square)
        assert board.piece_at(move.to_square).piece_type == chess.KNIGHT
        assert victim_color != mover


def test_hanging_piece_moves_capture_an_undefended_major_piece():
    cases = cases_by_id()
    expected = {
        "undefended-queen-rook-capture-001": "a1a8",
        "black-knight-captures-hanging-rook-001": "c6e5",
    }
    for position_id, uci in expected.items():
        board = chess.Board(cases[position_id].fen)
        move = chess.Move.from_uci(uci)
        victim = board.piece_at(move.to_square)
        assert victim is not None
        assert victim.piece_type in {chess.QUEEN, chess.ROOK}
        assert not board.attackers(not board.turn, move.to_square)
        board.push(move)
        assert board.piece_at(move.to_square).color == not board.turn


def test_pin_examples_capture_the_absolutely_pinned_piece():
    cases = cases_by_id()
    expected = {
        "rook-captures-pinned-rook-001": ("e1e7", chess.BLACK),
        "black-rook-captures-absolutely-pinned-rook-001": ("e8e2", chess.WHITE),
    }
    for position_id, (uci, pinned_color) in expected.items():
        board = chess.Board(cases[position_id].fen)
        move = chess.Move.from_uci(uci)
        assert board.is_pinned(pinned_color, move.to_square)
        board.push(move)
        assert board.piece_at(move.to_square).piece_type == chess.ROOK


def test_both_rook_skewers_check_the_king_with_queen_behind():
    cases = cases_by_id()
    expected = {
        "white-rook-skewers-king-and-queen-001": ("b1a1", chess.BLACK, chess.A6, chess.A8),
        "black-rook-skewers-king-and-queen-001": ("b8a8", chess.WHITE, chess.A3, chess.A1),
    }
    for position_id, (uci, victim_color, king_square, queen_square) in expected.items():
        board = chess.Board(cases[position_id].fen)
        move = chess.Move.from_uci(uci)
        board.push(move)
        rook_square = move.to_square
        assert board.is_check()
        assert board.piece_at(king_square) == chess.Piece(chess.KING, victim_color)
        assert board.piece_at(queen_square) == chess.Piece(chess.QUEEN, victim_color)
        assert chess.square_file(rook_square) == chess.square_file(king_square)
        assert chess.square_file(king_square) == chess.square_file(queen_square)
        assert min(chess.square_rank(rook_square), chess.square_rank(queen_square)) < chess.square_rank(king_square) < max(
            chess.square_rank(rook_square), chess.square_rank(queen_square)
        )


def test_discovered_attack_move_uncovers_rook_check_and_attacks_queen():
    board, move, mover = play_annotated_move("white-knight-discovered-check-queen-attack-001")
    king_square = board.king(not mover)
    queen_square = chess.H7
    assert move == chess.Move.from_uci("e4f6")
    assert board.is_check()
    assert board.piece_at(chess.E1) == chess.Piece(chess.ROOK, mover)
    assert board.is_attacked_by(mover, king_square)
    assert board.piece_at(move.to_square) == chess.Piece(chess.KNIGHT, mover)
    assert board.is_attacked_by(mover, queen_square)
    assert board.piece_at(queen_square) == chess.Piece(chess.QUEEN, not mover)


def test_defensive_resource_removes_the_checking_rook_and_resolves_check():
    case = cases_by_id()["black-knight-captures-checking-rook-001"]
    board = chess.Board(case.fen)
    move = chess.Move.from_uci("c2e1")
    assert board.is_check()
    assert board.piece_at(move.to_square) == chess.Piece(chess.ROOK, chess.WHITE)
    board.push(move)
    assert not board.is_check()
    assert board.piece_at(move.to_square) == chess.Piece(chess.KNIGHT, chess.BLACK)


def test_both_promotion_tactics_promote_to_queen_with_check():
    cases = cases_by_id()
    expected = {
        "white-pawn-promotes-with-check-001": ("a7a8q", chess.WHITE),
        "black-pawn-promotes-with-check-001": ("a2a1q", chess.BLACK),
    }
    for position_id, (uci, promoting_color) in expected.items():
        board = chess.Board(cases[position_id].fen)
        move = chess.Move.from_uci(uci)
        assert move.promotion == chess.QUEEN
        board.push(move)
        assert board.piece_at(move.to_square) == chess.Piece(chess.QUEEN, promoting_color)
        assert board.is_check()
