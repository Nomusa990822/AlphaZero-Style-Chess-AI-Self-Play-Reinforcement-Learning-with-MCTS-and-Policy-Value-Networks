"""Regression tests for the side-to-move and colour-mirror contracts.

These tests validate representation and value-perspective invariants. They do
not assert that an unconstrained neural network must itself be mirror-equivariant.
"""
import chess
import numpy as np

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.node import MCTSNode
from src.mcts.search import MCTS
from src.training.self_play import SelfPlayGenerator


def _mirror_move(move: chess.Move) -> chess.Move:
    """Apply python-chess Board.mirror()'s vertical square reflection."""
    return chess.Move(
        chess.square_mirror(move.from_square),
        chess.square_mirror(move.to_square),
        promotion=move.promotion,
        drop=move.drop,
    )


def test_board_encoder_obeys_documented_colour_mirror_transform():
    boards = [
        chess.Board(),
        chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"),
        chess.Board("8/P7/8/8/8/8/8/k6K w - - 0 1"),
    ]
    en_passant = chess.Board()
    for uci in ("e2e4", "a7a6", "e4e5", "d7d5"):
        en_passant.push_uci(uci)
    boards.append(en_passant)

    encoder = BoardEncoder()
    for board in boards:
        original = encoder.encode(board)
        mirrored = encoder.encode(board.mirror())
        expected = np.zeros_like(original)

        # Colour-specific piece planes exchange and ranks are reflected.
        for piece_plane in range(6):
            expected[piece_plane] = original[piece_plane + 6, ::-1, :]
            expected[piece_plane + 6] = original[piece_plane, ::-1, :]

        # Board.mirror() swaps the side to move and both colours' rights.
        expected[12] = 1.0 - original[12]
        expected[13] = original[15]
        expected[14] = original[16]
        expected[15] = original[13]
        expected[16] = original[14]

        # Move counters are invariant; en-passant square is rank-reflected.
        expected[17] = original[17]
        expected[18] = original[18]
        expected[19] = original[19, ::-1, :]

        np.testing.assert_array_equal(mirrored, expected)


def test_move_encoding_round_trips_every_legal_move_after_colour_mirroring():
    boards = [
        chess.Board(),
        chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"),
        chess.Board("8/P7/8/8/8/8/8/k6K w - - 0 1"),
        chess.Board("k6K/8/8/8/8/8/p7/8 b - - 0 1"),
    ]
    en_passant = chess.Board()
    for uci in ("e2e4", "a7a6", "e4e5", "d7d5"):
        en_passant.push_uci(uci)
    boards.append(en_passant)

    encoding = MoveEncoding()
    for board in boards:
        mirrored = board.mirror()
        mirrored_moves = {
            move.uci(): encoding.move_to_tensor_index(move, mirrored)
            for move in mirrored.legal_moves
        }
        for move in board.legal_moves:
            original_index = encoding.move_to_tensor_index(move, board)
            assert encoding.tensor_index_to_move(original_index, board) == move

            expected_mirror = _mirror_move(move)
            assert expected_mirror in mirrored.legal_moves
            mirrored_index = encoding.move_to_tensor_index(
                expected_mirror, mirrored
            )
            assert encoding.tensor_index_to_move(
                mirrored_index, mirrored
            ) == expected_mirror
            assert expected_mirror.uci() in mirrored_moves


def test_value_targets_are_invariant_for_colour_mirrored_game_outcomes():
    generator = SelfPlayGenerator(inference=None, move_encoding=MoveEncoding())
    boards = [chess.Board(), chess.Board()]
    boards[1].push_uci("e2e4")

    for board in boards:
        mirrored = board.mirror()
        assert mirrored.turn != board.turn
        for white_value in (-1.0, 0.0, 1.0):
            original_target = generator._value_for_player(
                white_value, board.turn
            )
            mirrored_white_value = -white_value
            mirrored_target = generator._value_for_player(
                mirrored_white_value, mirrored.turn
            )
            assert original_target == mirrored_target


def test_mcts_backup_alternates_value_perspective_by_ply():
    encoding = MoveEncoding()
    board = chess.Board()
    root = MCTSNode(board=board.copy())
    board.push_uci("e2e4")
    child = MCTSNode(board=board.copy(), parent=root)
    board.push_uci("e7e5")
    leaf = MCTSNode(board=board.copy(), parent=child)

    search = MCTS(
        inference=None,
        move_encoding=encoding,
    )
    search._backpropagate([root, child, leaf], leaf_value=0.75)

    assert leaf.q_value == 0.75
    assert child.q_value == -0.75
    assert root.q_value == 0.75


def test_terminal_value_is_invariant_under_colour_mirror():
    checkmated = chess.Board("7k/5Q2/7K/8/8/8/8/8 b - - 0 1")
    mirrored = checkmated.mirror()

    assert checkmated.is_checkmate()
    assert mirrored.is_checkmate()
    assert MCTSNode(checkmated).terminal_value() == -1.0
    assert MCTSNode(mirrored).terminal_value() == -1.0
