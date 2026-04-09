"""
Stage 1 placeholder for future state tracking utilities.

This module can later be extended to support:
- repetition-aware history stacks
- feature history planes
- game trajectory packaging for self-play
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import chess


@dataclass
class StateManager:
    """
    Tracks FEN history for a game.
    """
    fen_history: List[str] = field(default_factory=list)

    def record(self, board: chess.Board) -> None:
        """
        Store the current FEN in history.
        """
        self.fen_history.append(board.fen())

    def reset(self) -> None:
        """
        Clear tracked history.
        """
        self.fen_history.clear()

    def last_fen(self) -> str | None:
        """
        Return most recent stored FEN.
        """
        if not self.fen_history:
            return None
        return self.fen_history[-1]

    def num_states(self) -> int:
        """
        Number of stored positions.
        """
        return len(self.fen_history)
