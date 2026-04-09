"""
Move encoding helpers for AlphaZero-style chess.

For Stage 1, we create:
- a stable action space
- move <-> index mapping
- legal move mask generation

To keep the project practical and clean, Stage 1 uses a simple universal
move space based on all possible UCI move strings across:
- from-square: 64
- to-square: 64
- promotions: optional [q, r, b, n]

This is not the compressed AlphaZero 8x8x73 scheme yet, but it is:
- much easier to debug
- ideal for early development
- perfectly fine as a learning and portfolio version

Approximate action space:
64 * 64 + promotion variants
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import chess


PROMOTION_PIECES = [None, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
PROMOTION_TO_SUFFIX = {
    chess.QUEEN: "q",
    chess.ROOK: "r",
    chess.BISHOP: "b",
    chess.KNIGHT: "n",
}
SUFFIX_TO_PROMOTION = {v: k for k, v in PROMOTION_TO_SUFFIX.items()}


class MoveEncoding:
    """
    Handles move-index mapping for a universal move action space.
    """

    def __init__(self) -> None:
        self.index_to_move: List[str] = []
        self.move_to_index: Dict[str, int] = {}
        self._build_action_space()

    def _build_action_space(self) -> None:
        """
        Build a deterministic global move vocabulary.
        """
        all_moves: List[str] = []

        for from_sq in chess.SQUARES:
            for to_sq in chess.SQUARES:
                from_name = chess.square_name(from_sq)
                to_name = chess.square_name(to_sq)

                # Non-promotion move
                all_moves.append(f"{from_name}{to_name}")

                # Possible promotions if the move reaches back rank
                to_rank = chess.square_rank(to_sq)
                if to_rank in (0, 7):
                    for promo_piece in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                        suffix = PROMOTION_TO_SUFFIX[promo_piece]
                        all_moves.append(f"{from_name}{to_name}{suffix}")

        # Remove duplicates while preserving order
        seen = set()
        unique_moves = []
        for move in all_moves:
            if move not in seen:
                seen.add(move)
                unique_moves.append(move)

        self.index_to_move = unique_moves
        self.move_to_index = {move: idx for idx, move in enumerate(self.index_to_move)}

    @property
    def action_size(self) -> int:
        """
        Total number of actions in the universal move space.
        """
        return len(self.index_to_move)

    def uci_to_index(self, move_uci: str) -> int:
        """
        Convert UCI move string to action index.

        Args:
            move_uci: UCI move string

        Returns:
            Integer action index

        Raises:
            KeyError: If the move is not in the action space
        """
        if move_uci not in self.move_to_index:
            raise KeyError(f"Move not found in action space: {move_uci}")
        return self.move_to_index[move_uci]

    def index_to_uci(self, index: int) -> str:
        """
        Convert action index back to UCI move string.

        Args:
            index: Action index

        Returns:
            UCI move string

        Raises:
            IndexError: If index is out of range
        """
        return self.index_to_move[index]

    def move_to_tensor_index(self, move: chess.Move) -> int:
        """
        Convert python-chess Move to action index.

        Args:
            move: chess.Move object

        Returns:
            Integer action index
        """
        return self.uci_to_index(move.uci())

    def tensor_index_to_move(self, index: int) -> chess.Move:
        """
        Convert action index into a python-chess Move.

        Args:
            index: Integer action index

        Returns:
            chess.Move object
        """
        return chess.Move.from_uci(self.index_to_uci(index))

    def legal_move_indices(self, board: chess.Board) -> List[int]:
        """
        Get action indices for all legal moves in a position.

        Args:
            board: python-chess Board

        Returns:
            List of action indices
        """
        return [self.move_to_tensor_index(move) for move in board.legal_moves]

    def legal_moves_mask(self, board: chess.Board) -> List[int]:
        """
        Create a binary mask over the action space.

        Args:
            board: python-chess Board

        Returns:
            List of 0/1 integers of length action_size
        """
        mask = [0] * self.action_size
        for move in board.legal_moves:
            idx = self.move_to_tensor_index(move)
            mask[idx] = 1
        return mask

    def decode_best_legal_move(
        self,
        policy_logits: List[float],
        board: chess.Board
    ) -> Optional[chess.Move]:
        """
        Select the highest-scoring legal move from a policy vector.

        Args:
            policy_logits: Scores for the full action space
            board: Current board

        Returns:
            Best legal chess.Move, or None if no legal moves exist
        """
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        best_move = None
        best_score = float("-inf")

        for move in legal_moves:
            idx = self.move_to_tensor_index(move)
            score = policy_logits[idx]
            if score > best_score:
                best_score = score
                best_move = move

        return best_move
