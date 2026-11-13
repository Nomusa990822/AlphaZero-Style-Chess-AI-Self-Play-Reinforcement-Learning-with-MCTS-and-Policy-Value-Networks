"""
Encodes a chess.Board into a tensor suitable for neural networks.

Stage 1 encoder output shape:
(20, 8, 8)

Planes:
0  - White pawns
1  - White knights
2  - White bishops
3  - White rooks
4  - White queens
5  - White king
6  - Black pawns
7  - Black knights
8  - Black bishops
9  - Black rooks
10 - Black queens
11 - Black king
12 - Side to move (all ones if white to move, else zeros)
13 - White kingside castling rights
14 - White queenside castling rights
15 - Black kingside castling rights
16 - Black queenside castling rights
17 - Halfmove clock normalized
18 - Fullmove number normalized
19 - En-passant target square (one-hot)

This is a simplified AlphaZero-style starting point.
"""

from __future__ import annotations

from typing import Dict, Tuple

import chess
import numpy as np


PIECE_TO_PLANE: Dict[Tuple[bool, int], int] = {
    (chess.WHITE, chess.PAWN): 0,
    (chess.WHITE, chess.KNIGHT): 1,
    (chess.WHITE, chess.BISHOP): 2,
    (chess.WHITE, chess.ROOK): 3,
    (chess.WHITE, chess.QUEEN): 4,
    (chess.WHITE, chess.KING): 5,
    (chess.BLACK, chess.PAWN): 6,
    (chess.BLACK, chess.KNIGHT): 7,
    (chess.BLACK, chess.BISHOP): 8,
    (chess.BLACK, chess.ROOK): 9,
    (chess.BLACK, chess.QUEEN): 10,
    (chess.BLACK, chess.KING): 11,
}


class BoardEncoder:
    """
    Converts python-chess boards into neural network tensor inputs.
    """

    NUM_PLANES = 20
    BOARD_SIZE = 8

    @staticmethod
    def square_to_coords(square: chess.Square) -> Tuple[int, int]:
        """
        Convert a chess square index to tensor coordinates.

        Mapping:
        - rank 8 at row 0
        - rank 1 at row 7
        - file a at col 0
        - file h at col 7

        Args:
            square: python-chess square index

        Returns:
            (row, col)
        """
        rank = chess.square_rank(square)
        file_ = chess.square_file(square)
        row = 7 - rank
        col = file_
        return row, col

    def encode(self, board: chess.Board) -> np.ndarray:
        """
        Encode a board into a float32 tensor of shape (20, 8, 8).

        Args:
            board: python-chess Board object

        Returns:
            NumPy array of shape (20, 8, 8), dtype float32
        """
        planes = np.zeros(
            (self.NUM_PLANES, self.BOARD_SIZE, self.BOARD_SIZE),
            dtype=np.float32
        )

        # Piece placement planes
        for square, piece in board.piece_map().items():
            row, col = self.square_to_coords(square)
            plane_idx = PIECE_TO_PLANE[(piece.color, piece.piece_type)]
            planes[plane_idx, row, col] = 1.0

        # Side to move
        if board.turn == chess.WHITE:
            planes[12, :, :] = 1.0

        # Castling rights
        if board.has_kingside_castling_rights(chess.WHITE):
            planes[13, :, :] = 1.0
        if board.has_queenside_castling_rights(chess.WHITE):
            planes[14, :, :] = 1.0
        if board.has_kingside_castling_rights(chess.BLACK):
            planes[15, :, :] = 1.0
        if board.has_queenside_castling_rights(chess.BLACK):
            planes[16, :, :] = 1.0

        # Clocks / move counters
        # Light normalization for stability
        planes[17, :, :] = min(board.halfmove_clock / 100.0, 1.0)
        planes[18, :, :] = min(board.fullmove_number / 200.0, 1.0)

        if board.ep_square is not None:
            ep_row, ep_col = self.square_to_coords(board.ep_square)
            planes[19, ep_row, ep_col] = 1.0

        return planes

    def encode_batch(self, boards: list[chess.Board]) -> np.ndarray:
        """
        Encode a batch of boards.

        Args:
            boards: List of python-chess Board objects

        Returns:
            NumPy array of shape (batch_size, 20, 8, 8)
        """
        return np.stack([self.encode(board) for board in boards], axis=0)
