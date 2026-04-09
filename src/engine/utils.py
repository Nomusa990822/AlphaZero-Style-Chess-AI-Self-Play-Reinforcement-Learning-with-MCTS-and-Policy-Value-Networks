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


def pretty_board(board) -> str:
    """
    Render a clean ASCII chess board with ranks/files and grid lines.
    All pieces shown in white text style (no colors).

    Example style:
        a   b   c   d   e   f   g   h
      ---------------------------------
    8 | bR | bN | bB | bQ | bK | bB | bN | bR | 8
      ---------------------------------
    ...
    """

    # Piece mapping
    piece_map = {
        'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK',
        'p': 'bP', 'n': 'bN', 'b': 'bB', 'r': 'bR', 'q': 'bQ', 'k': 'bK'
    }

    files = "a   b   c   d   e   f   g   h"
    separator = "  -----------------------------------------"

    lines = []
    lines.append("    " + files)
    lines.append(separator)

    for rank in range(8, 0, -1):
        row = f"{rank} |"

        for file_idx in range(8):
            square = f"{chr(ord('a') + file_idx)}{rank}"
            piece = board.piece_at(
                __import__("chess").parse_square(square)
            )

            if piece:
                symbol = piece.symbol()
                row += f" {piece_map[symbol]} |"
            else:
                row += "    |"

        row += f" {rank}"
        lines.append(row)
        lines.append(separator)

    lines.append("    " + files)

    return "\n".join(lines)
