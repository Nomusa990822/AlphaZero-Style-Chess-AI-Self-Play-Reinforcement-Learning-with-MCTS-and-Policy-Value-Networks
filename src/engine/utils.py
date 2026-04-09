"""
Small utility helpers for chess engine development.
"""

from __future__ import annotations

from typing import Optional

import chess


def result_to_value(result: Optional[str]) -> float:
    """
    Convert a chess result string into a scalar value
    from White's perspective.

    Args:
        result: '1-0', '0-1', '1/2-1/2', or None

    Returns:
        1.0  for white win
        -1.0 for black win
        0.0  for draw or ongoing game
    """
    if result == "1-0":
        return 1.0
    if result == "0-1":
        return -1.0
    if result == "1/2-1/2":
        return 0.0
    return 0.0


def value_from_perspective(result: Optional[str], board_turn: bool) -> float:
    """
    Convert a game result into a value from the current player's perspective.

    Args:
        result: Standard chess result string
        board_turn: True if White to move, False if Black to move

    Returns:
        Value in [-1, 1] from side-to-move perspective.
    """
    white_value = result_to_value(result)
    return white_value if board_turn == chess.WHITE else -white_value


def pretty_print_board(board: chess.Board) -> str:
    """
    Return an ASCII representation of the board.

    Args:
        board: python-chess board

    Returns:
        Formatted string
    """
    return str(board)


def fen_side_to_move(fen: str) -> str:
    """
    Extract whose turn it is from a FEN string.

    Args:
        fen: Valid FEN string

    Returns:
        'white' or 'black'
    """
    board = chess.Board(fen)
    return "white" if board.turn == chess.WHITE else "black"
