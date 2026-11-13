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


_EXCHANGE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20_000,
}


def static_exchange_evaluation(
    board: chess.Board,
    move: chess.Move,
    max_capture_nodes: int = 128,
) -> int | None:
    """
    Estimate the material balance of a capture sequence on move.to_square.

    The supplied move must be legal. After making it, both sides may stop or
    continue capturing the piece occupying the destination square. Only legal
    recaptures are considered, so pinned pieces and illegal king captures are
    excluded by python-chess.

    The result is measured in centipawn-like material units from the original
    mover's perspective. Positive values favour the move; negative values mean
    the opponent can win material in the exchange. Promotions include their
    material gain. En-passant uses the actual captured-pawn square.

    Returns None if the bounded recapture search exhausts its node budget.
    Unknown is deliberately distinct from a zero or losing exchange.
    """
    if max_capture_nodes < 1:
        raise ValueError("max_capture_nodes must be at least 1")
    if move not in board.legal_moves:
        raise ValueError("move must be legal in the supplied position")

    def piece_value(piece: chess.Piece | None) -> int:
        if piece is None:
            return 0
        return _EXCHANGE_VALUES[piece.piece_type]

    def promotion_gain(candidate: chess.Move) -> int:
        if candidate.promotion is None:
            return 0
        return _EXCHANGE_VALUES[candidate.promotion] - _EXCHANGE_VALUES[chess.PAWN]

    if board.is_en_passant(move):
        captured_square = move.to_square - 8 if board.turn == chess.WHITE else move.to_square + 8
    else:
        captured_square = move.to_square

    captured_piece = board.piece_at(captured_square)
    initial_gain = piece_value(captured_piece) + promotion_gain(move)
    target_square = move.to_square
    nodes = 0

    def best_recapture() -> int | None:
        nonlocal nodes
        best_gain = 0  # Either side may decline further exchanges.
        for reply in list(board.legal_moves):
            if reply.to_square != target_square or not board.is_capture(reply):
                continue
            if nodes >= max_capture_nodes:
                return None
            nodes += 1
            victim = board.piece_at(target_square)
            immediate_gain = piece_value(victim) + promotion_gain(reply)
            board.push(reply)
            try:
                continuation = best_recapture()
            finally:
                board.pop()
            if continuation is None:
                return None
            best_gain = max(best_gain, immediate_gain - continuation)
        return best_gain

    board.push(move)
    try:
        opponent_gain = best_recapture()
    finally:
        board.pop()

    if opponent_gain is None:
        return None
    return initial_gain - opponent_gain
