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
        "knight-fork-king-queen-001": ("c5d7", chess.BLACK, chess.F8, chess.F6),
        "black-knight-checking-fork-king-queen-001": ("c6d4", chess.WHITE, chess.F3, chess.E2),
    }
    for position_id, (uci, victim_color, king_square, queen_square) in expected.items():
        case = cases[position_id]
        board = chess.Board(case.fen)
        mover = board.turn
        move = chess.Move.from_uci(uci)
        board.push(move)
        assert move.to_square in board.attackers(mover, king_square)
        assert move.to_square in board.attackers(mover, queen_square)
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
        assert board.piece_at(move.to_square).color == (not board.turn)


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
    assert chess.E1 in board.attackers(mover, king_square)
    assert board.piece_at(move.to_square) == chess.Piece(chess.KNIGHT, mover)
    assert move.to_square in board.attackers(mover, queen_square)
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


def test_non_checking_double_attack_targets_queen_and_rook():
    case = cases_by_id()["white-knight-double-attack-queen-rook-001"]
    board = chess.Board(case.fen)
    move = chess.Move.from_uci("c5d7")
    assert case.motif == "double_attack"
    assert board.turn == chess.WHITE
    assert move in board.legal_moves
    board.push(move)
    assert not board.is_check()
    assert board.piece_at(chess.F6) == chess.Piece(chess.QUEEN, chess.BLACK)
    assert board.piece_at(chess.F8) == chess.Piece(chess.ROOK, chess.BLACK)
    assert move.to_square in board.attackers(chess.WHITE, chess.F6)
    assert move.to_square in board.attackers(chess.WHITE, chess.F8)



def test_black_bishop_deflection_draws_white_queen_off_mating_square():
    case = cases_by_id()["black-bishop-deflects-queen-from-mating-square-001"]
    board = chess.Board(case.fen)
    move = chess.Move.from_uci("a1d4")

    assert board.turn == chess.BLACK
    assert case.motif == "deflection"
    assert move in board.legal_moves
    board.push(move)
    assert board.is_check()
    assert board.piece_at(chess.D4) == chess.Piece(chess.BISHOP, chess.BLACK)

    # The queen is the only white piece able to answer this bishop check
    # by capturing the checking bishop in the supplied tactical line.
    reply = chess.Move.from_uci("c4d4")
    assert reply in board.legal_moves
    board.push(reply)
    assert board.piece_at(chess.D4) == chess.Piece(chess.QUEEN, chess.WHITE)
    assert chess.F1 not in board.attacks(chess.D4)

    mating_move = chess.Move.from_uci("f3f1")
    assert mating_move in board.legal_moves
    board.push(mating_move)
    assert board.is_checkmate()



def test_white_queen_decoy_lures_king_into_rook_mate():
    case = cases_by_id()["white-queen-decoy-draws-king-into-rook-mate-001"]
    board = chess.Board(case.fen)
    sacrifice = chess.Move.from_uci("c2h7")

    assert case.motif == "decoy"
    assert board.turn == chess.WHITE
    assert sacrifice in board.legal_moves
    board.push(sacrifice)
    assert board.is_check()
    assert board.piece_at(chess.H7) == chess.Piece(chess.QUEEN, chess.WHITE)

    king_capture = chess.Move.from_uci("h8h7")
    assert king_capture in board.legal_moves
    board.push(king_capture)
    assert board.piece_at(chess.H7) == chess.Piece(chess.KING, chess.BLACK)

    mating_rook_move = chess.Move.from_uci("d5h5")
    assert mating_rook_move in board.legal_moves
    board.push(mating_rook_move)
    assert board.is_checkmate()


def test_black_rook_removes_c4_pawn_defender_before_knight_mate():
    case = cases_by_id()["black-rook-removes-c4-pawn-defender-before-knight-mate-001"]
    board = chess.Board(case.fen)
    sacrifice = chess.Move.from_uci("c8c4")

    assert case.motif == "removal_of_defender"
    assert board.turn == chess.BLACK
    assert board.piece_at(chess.C4) == chess.Piece(chess.PAWN, chess.WHITE)
    assert chess.B5 in board.attacks(chess.C4)
    assert sacrifice in board.legal_moves
    board.push(sacrifice)
    assert board.is_check()
    assert board.piece_at(chess.C4) == chess.Piece(chess.ROOK, chess.BLACK)

    recapture = chess.Move.from_uci("c2c4")
    assert recapture in board.legal_moves
    board.push(recapture)
    assert board.piece_at(chess.C4) == chess.Piece(chess.ROOK, chess.WHITE)

    mating_move = chess.Move.from_uci("d6b5")
    assert mating_move in board.legal_moves
    board.push(mating_move)
    assert board.is_checkmate()



def test_white_rook_interference_blocks_queen_and_creates_back_rank_mate():
    case = cases_by_id()["white-rook-interference-diverts-knight-from-queen-defence-001"]
    board = chess.Board(case.fen)
    move = chess.Move.from_uci("d1d8")

    assert case.motif == "interference"
    assert board.turn == chess.WHITE
    assert move in board.legal_moves
    assert board.piece_at(chess.A8) == chess.Piece(chess.KING, chess.BLACK)
    assert board.piece_at(chess.E8) == chess.Piece(chess.QUEEN, chess.BLACK)
    assert board.piece_at(chess.H8) == chess.Piece(chess.ROOK, chess.BLACK)
    assert board.piece_at(chess.E6) == chess.Piece(chess.KNIGHT, chess.BLACK)
    assert board.piece_at(chess.G5) == chess.Piece(chess.BISHOP, chess.WHITE)

    # Rd8+ places the rook on the queen's eighth-rank line and checks the king.
    board.push(move)
    assert board.is_check()
    assert board.piece_at(chess.D8) == chess.Piece(chess.ROOK, chess.WHITE)

    # The knight can interpose by capturing the rook. It then blocks its own
    # queen's route to c8, allowing the white queen's mating move.
    knight_capture = chess.Move.from_uci("e6d8")
    assert knight_capture in board.legal_moves
    board.push(knight_capture)
    assert board.piece_at(chess.D8) == chess.Piece(chess.KNIGHT, chess.BLACK)
    assert chess.Move.from_uci("c2c8") in board.legal_moves
    board.push(chess.Move.from_uci("c2c8"))
    assert board.is_checkmate()

    # The queen's alternative capture of the checking rook is tactically
    # refuted by the bishop on g5, which protects d8.
    alternative = chess.Board(case.fen)
    alternative.push(move)
    queen_capture = chess.Move.from_uci("e8d8")
    assert queen_capture in alternative.legal_moves
    alternative.push(queen_capture)
    bishop_recapture = chess.Move.from_uci("g5d8")
    assert bishop_recapture in alternative.legal_moves
    alternative.push(bishop_recapture)
    assert alternative.piece_at(chess.D8) == chess.Piece(chess.BISHOP, chess.WHITE)
    assert alternative.piece_at(chess.D8).color == chess.WHITE
