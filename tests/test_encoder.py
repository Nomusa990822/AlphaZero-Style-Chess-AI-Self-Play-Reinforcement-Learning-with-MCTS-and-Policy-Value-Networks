import chess
import numpy as np

from src.engine.encoder import BoardEncoder


def test_encoder_output_shape():
    board = chess.Board()
    encoder = BoardEncoder()
    tensor = encoder.encode(board)

    assert tensor.shape == (19, 8, 8)
    assert tensor.dtype == np.float32


def test_white_pawn_plane_start_position():
    board = chess.Board()
    encoder = BoardEncoder()
    tensor = encoder.encode(board)

    # White pawns on rank 2 => row 6
    for col in range(8):
        assert tensor[0, 6, col] == 1.0


def test_black_pawn_plane_start_position():
    board = chess.Board()
    encoder = BoardEncoder()
    tensor = encoder.encode(board)

    # Black pawns on rank 7 => row 1
    for col in range(8):
        assert tensor[6, 1, col] == 1.0


def test_side_to_move_plane_for_white():
    board = chess.Board()
    encoder = BoardEncoder()
    tensor = encoder.encode(board)

    assert np.all(tensor[12] == 1.0)


def test_side_to_move_plane_for_black():
    board = chess.Board()
    board.push_uci("e2e4")
    encoder = BoardEncoder()
    tensor = encoder.encode(board)

    assert np.all(tensor[12] == 0.0)


def test_castling_rights_planes_initial_position():
    board = chess.Board()
    encoder = BoardEncoder()
    tensor = encoder.encode(board)

    assert np.all(tensor[13] == 1.0)
    assert np.all(tensor[14] == 1.0)
    assert np.all(tensor[15] == 1.0)
    assert np.all(tensor[16] == 1.0)


def test_castling_rights_change_after_king_move():
    board = chess.Board()
    board.push_uci("e2e4")
    board.push_uci("e7e5")
    board.push_uci("e1e2")

    encoder = BoardEncoder()
    tensor = encoder.encode(board)

    assert np.all(tensor[13] == 0.0)
    assert np.all(tensor[14] == 0.0)


def test_encode_batch_shape():
    boards = [chess.Board(), chess.Board()]
    encoder = BoardEncoder()
    batch = encoder.encode_batch(boards)

    assert batch.shape == (2, 19, 8, 8)


def test_specific_piece_location():
    board = chess.Board()
    encoder = BoardEncoder()
    tensor = encoder.encode(board)

    # White king starts on e1 => row 7, col 4
    assert tensor[5, 7, 4] == 1.0

    # Black king starts on e8 => row 0, col 4
    assert tensor[11, 0, 4] == 1.0
