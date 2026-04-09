import chess

from src.engine.move_encoding import MoveEncoding


def test_action_space_exists():
    encoder = MoveEncoding()
    assert encoder.action_size > 0


def test_uci_to_index_and_back():
    encoder = MoveEncoding()
    move = "e2e4"

    idx = encoder.uci_to_index(move)
    decoded = encoder.index_to_uci(idx)

    assert decoded == move


def test_chess_move_to_index_and_back():
    encoder = MoveEncoding()
    move = chess.Move.from_uci("g1f3")

    idx = encoder.move_to_tensor_index(move)
    decoded_move = encoder.tensor_index_to_move(idx)

    assert decoded_move.uci() == "g1f3"


def test_legal_move_indices_match_start_position():
    board = chess.Board()
    encoder = MoveEncoding()

    legal_indices = encoder.legal_move_indices(board)

    assert len(legal_indices) == 20


def test_legal_move_mask_marks_only_legal_moves():
    board = chess.Board()
    encoder = MoveEncoding()

    mask = encoder.legal_moves_mask(board)
    assert len(mask) == encoder.action_size
    assert sum(mask) == 20

    e2e4_idx = encoder.uci_to_index("e2e4")
    assert mask[e2e4_idx] == 1


def test_promotion_move_supported():
    encoder = MoveEncoding()
    move = "a7a8q"

    idx = encoder.uci_to_index(move)
    decoded = encoder.index_to_uci(idx)

    assert decoded == move


def test_decode_best_legal_move():
    board = chess.Board()
    encoder = MoveEncoding()

    logits = [0.0] * encoder.action_size
    best_idx = encoder.uci_to_index("e2e4")
    logits[best_idx] = 10.0

    best_move = encoder.decode_best_legal_move(logits, board)

    assert best_move is not None
    assert best_move.uci() == "e2e4"
