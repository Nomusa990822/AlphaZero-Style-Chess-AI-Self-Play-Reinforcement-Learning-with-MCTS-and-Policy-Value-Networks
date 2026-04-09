import chess
import numpy as np

from src.engine.move_encoding import MoveEncoding


def test_action_space_size():
    encoder = MoveEncoding()
    assert encoder.action_size == 4672


def test_uci_to_index_and_back_start_position():
    encoder = MoveEncoding()
    board = chess.Board()

    move = "e2e4"
    idx = encoder.uci_to_index(move, board)
    decoded = encoder.index_to_uci(idx, board)

    assert decoded == move


def test_knight_move_to_index_and_back():
    encoder = MoveEncoding()
    board = chess.Board()

    move = chess.Move.from_uci("g1f3")
    idx = encoder.move_to_tensor_index(move, board)
    decoded_move = encoder.tensor_index_to_move(idx, board)

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
    assert isinstance(mask, np.ndarray)
    assert mask.shape == (encoder.action_size,)
    assert float(mask.sum()) == 20.0

    e2e4_idx = encoder.uci_to_index("e2e4", board)
    assert mask[e2e4_idx] == 1.0


def test_white_queen_promotion_supported():
    encoder = MoveEncoding()
    board = chess.Board("8/P7/8/8/8/8/8/k6K w - - 0 1")

    move = "a7a8q"
    idx = encoder.uci_to_index(move, board)
    decoded = encoder.index_to_uci(idx, board)

    assert decoded == move


def test_white_underpromotion_supported():
    encoder = MoveEncoding()
    board = chess.Board("8/P7/8/8/8/8/8/k6K w - - 0 1")

    move = "a7a8n"
    idx = encoder.uci_to_index(move, board)
    decoded = encoder.index_to_uci(idx, board)

    assert decoded == move


def test_black_move_encoding_respects_turn_perspective():
    encoder = MoveEncoding()
    board = chess.Board()
    board.push_uci("e2e4")  # now black to move

    move = "e7e5"
    idx = encoder.uci_to_index(move, board)
    decoded = encoder.index_to_uci(idx, board)

    assert decoded == move


def test_decode_best_legal_move():
    board = chess.Board()
    encoder = MoveEncoding()

    logits = np.zeros(encoder.action_size, dtype=np.float32)
    best_idx = encoder.uci_to_index("e2e4", board)
    logits[best_idx] = 10.0

    best_move = encoder.decode_best_legal_move(logits, board)

    assert best_move is not None
    assert best_move.uci() == "e2e4"
