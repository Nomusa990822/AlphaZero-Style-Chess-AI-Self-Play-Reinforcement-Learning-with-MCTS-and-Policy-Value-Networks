"""
True AlphaZero-style chess move encoding.

Action space:
    8 x 8 x 73 = 4672

Encoding per origin square:
- 56 queen-like moves:
    8 directions x 7 distances
- 8 knight moves
- 9 underpromotion moves:
    3 directions x 3 promotion pieces (R, B, N)

This module maps between:
- python-chess Move / UCI
- flat action index in [0, 4671]

Notes:
- Promotions to queen are encoded as normal queen-like moves.
- Underpromotions are encoded in the final 9 planes.
- Castling is encoded as king moves (e1g1, e1c1, etc.).
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import chess
import numpy as np


class MoveEncoding:
    """
    AlphaZero-style 8x8x73 move encoder.
    """

    BOARD_SIZE = 8
    PLANES_PER_SQUARE = 73
    ACTION_SIZE = 8 * 8 * 73

    # Queen-like directions: N, NE, E, SE, S, SW, W, NW
    QUEEN_DIRECTIONS: list[tuple[int, int]] = [
        (-1, 0),   # N
        (-1, 1),   # NE
        (0, 1),    # E
        (1, 1),    # SE
        (1, 0),    # S
        (1, -1),   # SW
        (0, -1),   # W
        (-1, -1),  # NW
    ]

    # Knight moves
    KNIGHT_DELTAS: list[tuple[int, int]] = [
        (-2, -1),
        (-2, 1),
        (-1, 2),
        (1, 2),
        (2, 1),
        (2, -1),
        (1, -2),
        (-1, -2),
    ]

    # Underpromotion directions from White perspective:
    # left-diagonal, forward, right-diagonal
    UNDERPROMOTION_DIRECTIONS: list[tuple[int, int]] = [
        (-1, -1),
        (-1, 0),
        (-1, 1),
    ]

    UNDERPROMOTION_PIECES: list[int] = [
        chess.ROOK,
        chess.BISHOP,
        chess.KNIGHT,
    ]

    def __init__(self) -> None:
        self.action_size = self.ACTION_SIZE

    @staticmethod
    def square_to_coords(square: chess.Square) -> tuple[int, int]:
        """
        Convert python-chess square to tensor-style coordinates.

        Returns:
            row, col where:
            - row 0 is rank 8
            - row 7 is rank 1
            - col 0 is file a
            - col 7 is file h
        """
        rank = chess.square_rank(square)
        file_ = chess.square_file(square)
        return 7 - rank, file_

    @staticmethod
    def coords_to_square(row: int, col: int) -> chess.Square:
        """
        Convert row, col back to python-chess square.
        """
        rank = 7 - row
        file_ = col
        return chess.square(file_, rank)

    @staticmethod
    def _rotate_for_black(row_delta: int, col_delta: int) -> tuple[int, int]:
        """
        Rotate move deltas so encoding is always from side-to-move perspective.

        For black, flip the board vertically and horizontally in move-space.
        """
        return -row_delta, -col_delta

    def _move_to_plane(
        self,
        board: chess.Board,
        from_square: chess.Square,
        to_square: chess.Square,
        promotion: Optional[int],
    ) -> int:
        """
        Convert a move into one of the 73 AlphaZero planes.

        Returns:
            plane index in [0, 72]

        Raises:
            ValueError if the move cannot be encoded.
        """
        from_row, from_col = self.square_to_coords(from_square)
        to_row, to_col = self.square_to_coords(to_square)

        row_delta = to_row - from_row
        col_delta = to_col - from_col

        # Normalize to side-to-move perspective
        if board.turn == chess.BLACK:
            row_delta, col_delta = self._rotate_for_black(row_delta, col_delta)

        # Underpromotions: only R, B, N get special planes
        if promotion in self.UNDERPROMOTION_PIECES:
            for dir_idx, (dr, dc) in enumerate(self.UNDERPROMOTION_DIRECTIONS):
                if (row_delta, col_delta) == (dr, dc):
                    piece_idx = self.UNDERPROMOTION_PIECES.index(promotion)
                    return 64 + dir_idx * 3 + piece_idx
            raise ValueError("Invalid underpromotion encoding.")

        # Queen-like moves: 56 planes
        for dir_idx, (dr, dc) in enumerate(self.QUEEN_DIRECTIONS):
            for distance in range(1, 8):
                if (row_delta, col_delta) == (dr * distance, dc * distance):
                    return dir_idx * 7 + (distance - 1)

        # Knight moves: 8 planes
        for knight_idx, (dr, dc) in enumerate(self.KNIGHT_DELTAS):
            if (row_delta, col_delta) == (dr, dc):
                return 56 + knight_idx

        raise ValueError(
            f"Move could not be encoded: from={chess.square_name(from_square)}, "
            f"to={chess.square_name(to_square)}, promotion={promotion}"
        )

    def _plane_to_move(
        self,
        board: chess.Board,
        from_square: chess.Square,
        plane: int,
    ) -> chess.Move:
        """
        Decode a plane index plus origin square into a chess.Move.

        Raises:
            ValueError if the decoded move is invalid.
        """
        from_row, from_col = self.square_to_coords(from_square)

        if 0 <= plane < 56:
            dir_idx = plane // 7
            distance = (plane % 7) + 1
            dr, dc = self.QUEEN_DIRECTIONS[dir_idx]
            row_delta = dr * distance
            col_delta = dc * distance
            promotion = None

        elif 56 <= plane < 64:
            knight_idx = plane - 56
            row_delta, col_delta = self.KNIGHT_DELTAS[knight_idx]
            promotion = None

        elif 64 <= plane < 73:
            under_idx = plane - 64
            dir_idx = under_idx // 3
            piece_idx = under_idx % 3
            row_delta, col_delta = self.UNDERPROMOTION_DIRECTIONS[dir_idx]
            promotion = self.UNDERPROMOTION_PIECES[piece_idx]

        else:
            raise ValueError(f"Plane index out of range: {plane}")

        # Undo normalization for black-to-move
        if board.turn == chess.BLACK:
            row_delta, col_delta = self._rotate_for_black(row_delta, col_delta)

        to_row = from_row + row_delta
        to_col = from_col + col_delta

        if not (0 <= to_row < 8 and 0 <= to_col < 8):
            raise ValueError("Decoded move lands off board.")

        to_square = self.coords_to_square(to_row, to_col)

        # Auto-handle queen promotion when pawn reaches back rank and no underpromotion set
        moving_piece = board.piece_at(from_square)
        if moving_piece is None:
            raise ValueError("No piece on from_square during decode.")

        if (
            moving_piece.piece_type == chess.PAWN
            and promotion is None
            and chess.square_rank(to_square) in (0, 7)
        ):
            promotion = chess.QUEEN

        return chess.Move(from_square, to_square, promotion=promotion)

    def move_to_tensor_index(self, move: chess.Move, board: chess.Board) -> int:
        """
        Convert a chess.Move into a flat AlphaZero action index.

        Args:
            move: chess.Move
            board: current board BEFORE the move is played
        """
        from_row, from_col = self.square_to_coords(move.from_square)
        plane = self._move_to_plane(
            board=board,
            from_square=move.from_square,
            to_square=move.to_square,
            promotion=move.promotion,
        )
        return (from_row * 8 + from_col) * 73 + plane

    def tensor_index_to_move(self, index: int, board: chess.Board) -> chess.Move:
        """
        Convert a flat action index into a chess.Move.

        Args:
            index: flat action index
            board: current board BEFORE the move is played
        """
        if not (0 <= index < self.action_size):
            raise IndexError(f"Index out of bounds: {index}")

        square_index, plane = divmod(index, 73)
        from_row, from_col = divmod(square_index, 8)
        from_square = self.coords_to_square(from_row, from_col)

        return self._plane_to_move(board=board, from_square=from_square, plane=plane)

    def uci_to_index(self, move_uci: str, board: chess.Board) -> int:
        """
        Convert UCI string to action index.
        """
        move = chess.Move.from_uci(move_uci)
        return self.move_to_tensor_index(move, board)

    def index_to_uci(self, index: int, board: chess.Board) -> str:
        """
        Convert action index to UCI string.
        """
        return self.tensor_index_to_move(index, board).uci()

    def legal_move_indices(self, board: chess.Board) -> List[int]:
        """
        Return flat action indices for all legal moves.
        """
        return [self.move_to_tensor_index(move, board) for move in board.legal_moves]

    def legal_moves_mask(self, board: chess.Board) -> np.ndarray:
        """
        Return binary mask over full action space.
        """
        mask = np.zeros(self.action_size, dtype=np.float32)
        for move in board.legal_moves:
            idx = self.move_to_tensor_index(move, board)
            mask[idx] = 1.0
        return mask

    def decode_best_legal_move(
        self,
        policy_logits: List[float] | np.ndarray,
        board: chess.Board,
    ) -> Optional[chess.Move]:
        """
        Select highest-scoring legal move under the policy vector.
        """
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        best_move = None
        best_score = float("-inf")

        for move in legal_moves:
            idx = self.move_to_tensor_index(move, board)
            score = float(policy_logits[idx])
            if score > best_score:
                best_score = score
                best_move = move

        return best_move
