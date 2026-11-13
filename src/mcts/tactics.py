"""
Exact shallow tactical checks used to preserve forced immediate checkmates.

These checks do not encode chess patterns or piece-specific heuristics. They
enumerate legal moves and ask the chess rules engine whether a move ends the
game by checkmate.
"""

from __future__ import annotations

import chess


def find_mate_in_one(board: chess.Board) -> list[chess.Move]:
    """Return every legal move that checkmates immediately, if any."""
    if board.is_game_over(claim_draw=True):
        return []

    mating_moves: list[chess.Move] = []
    for move in list(board.legal_moves):
        board.push(move)
        try:
            if board.is_checkmate():
                mating_moves.append(move)
        finally:
            board.pop()
    return mating_moves
