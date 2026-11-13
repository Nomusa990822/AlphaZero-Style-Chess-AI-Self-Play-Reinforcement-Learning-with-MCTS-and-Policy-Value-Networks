"""
Exact shallow tactical checks used to preserve immediate checkmates and avoid
moves that permit an opponent's immediate checkmate.

These checks enumerate legal moves and ask the chess rules engine whether a
move ends the game by checkmate. They do not encode piece-specific patterns.
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


def find_moves_avoiding_mate_in_one(board: chess.Board) -> list[chess.Move]:
    """
    Return legal moves that do not allow the opponent to checkmate next move.

    An empty result means every legal move permits mate in one (or the
    position is already over). Callers should fall back to their normal
    selection policy when no safe move exists, rather than pretending a
    forced loss can be avoided.
    """
    if board.is_game_over(claim_draw=True):
        return []

    safe_moves: list[chess.Move] = []
    for move in list(board.legal_moves):
        board.push(move)
        try:
            if board.is_game_over(claim_draw=True):
                # A move that ends the game cannot allow a reply.
                safe_moves.append(move)
            elif not find_mate_in_one(board):
                safe_moves.append(move)
        finally:
            board.pop()
    return safe_moves


def find_forced_mate_in_two(
    board: chess.Board,
    max_reply_checks: int = 512,
) -> list[chess.Move]:
    """
    Find root moves after which every legal opponent reply permits mate in one.

    At most max_reply_checks opponent replies are examined across the root
    position. If the budget interrupts a candidate, that candidate is
    discarded rather than treated as a proven forced mate. This conservative
    bound can miss a real mate-in-two in a high-branching position, but cannot
    promote an unverified candidate.
    """
    if max_reply_checks < 1:
        raise ValueError("max_reply_checks must be at least 1")
    if board.is_game_over(claim_draw=True):
        return []

    forced_mates: list[chess.Move] = []
    replies_checked = 0
    for move in list(board.legal_moves):
        board.push(move)
        try:
            if board.is_game_over(claim_draw=True):
                continue
            replies = list(board.legal_moves)
            if not replies:
                continue
            forces_mate = True
            candidate_complete = True
            for reply in replies:
                if replies_checked >= max_reply_checks:
                    candidate_complete = False
                    break
                replies_checked += 1
                board.push(reply)
                try:
                    if board.is_game_over(claim_draw=True) or not find_mate_in_one(board):
                        forces_mate = False
                        break
                finally:
                    board.pop()
            if candidate_complete and forces_mate:
                forced_mates.append(move)
            if replies_checked >= max_reply_checks:
                break
        finally:
            board.pop()
    return forced_mates
