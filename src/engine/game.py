"""
Core chess environment wrapper built on top of python-chess.

This module provides a clean interface for:
- resetting the game
- applying legal moves
- checking terminal states
- retrieving results
- cloning positions for search/training
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import chess


@dataclass
class GameState:
    """
    Lightweight snapshot of a chess game state.
    """
    fen: str
    turn: str
    is_terminal: bool
    result: Optional[str]
    legal_moves: List[str]


class ChessGame:
    """
    Wrapper around python-chess Board for easier integration
    with AlphaZero-style training and search code.
    """

    def __init__(self, fen: Optional[str] = None) -> None:
        """
        Initialize a chess board.

        Args:
            fen: Optional FEN string to start from a custom position.
        """
        self.board = chess.Board(fen) if fen else chess.Board()

    def reset(self) -> None:
        """
        Reset the board to the standard starting position.
        """
        self.board.reset()

    def copy(self) -> "ChessGame":
        """
        Create a deep copy of the game instance.

        Returns:
            A new ChessGame object with the same board state.
        """
        new_game = ChessGame()
        new_game.board = self.board.copy(stack=True)
        return new_game

    def get_fen(self) -> str:
        """
        Get the current board position in FEN format.

        Returns:
            Current FEN string.
        """
        return self.board.fen()

    def set_fen(self, fen: str) -> None:
        """
        Set the board to a given FEN position.

        Args:
            fen: Valid FEN string.
        """
        self.board.set_fen(fen)

    def current_player(self) -> str:
        """
        Get the side to move.

        Returns:
            'white' if White to move, otherwise 'black'.
        """
        return "white" if self.board.turn == chess.WHITE else "black"

    def legal_moves(self) -> List[chess.Move]:
        """
        Get all legal moves in the current position.

        Returns:
            List of legal chess.Move objects.
        """
        return list(self.board.legal_moves)

    def legal_moves_uci(self) -> List[str]:
        """
        Get all legal moves in UCI string format.

        Returns:
            List of legal move strings, e.g. ['e2e4', 'd2d4'].
        """
        return [move.uci() for move in self.board.legal_moves]

    def push(self, move: chess.Move) -> None:
        """
        Apply a legal move to the board.

        Args:
            move: A python-chess Move object.

        Raises:
            ValueError: If the move is illegal.
        """
        if move not in self.board.legal_moves:
            raise ValueError(f"Illegal move attempted: {move.uci()}")
        self.board.push(move)

    def push_uci(self, move_uci: str) -> None:
        """
        Apply a move given in UCI notation.

        Args:
            move_uci: Move string like 'e2e4'.

        Raises:
            ValueError: If the move string is invalid or illegal.
        """
        try:
            move = chess.Move.from_uci(move_uci)
        except ValueError as exc:
            raise ValueError(f"Invalid UCI move string: {move_uci}") from exc

        self.push(move)

    def pop(self) -> chess.Move:
        """
        Undo the last move.

        Returns:
            The move that was undone.

        Raises:
            IndexError: If there is no move to undo.
        """
        return self.board.pop()

    def is_terminal(self) -> bool:
        """
        Check if the game is over.

        Returns:
            True if the game is over, otherwise False.
        """
        return self.board.is_game_over()

    def result(self) -> Optional[str]:
        """
        Get the game result if terminal.

        Returns:
            One of:
            - '1-0'   : White wins
            - '0-1'   : Black wins
            - '1/2-1/2' : Draw
            - None    : If the game is not over
        """
        if not self.is_terminal():
            return None
        return self.board.result()

    def winner(self) -> Optional[str]:
        """
        Get the winner in human-readable form.

        Returns:
            'white', 'black', 'draw', or None if game is not over.
        """
        result = self.result()
        if result is None:
            return None
        if result == "1-0":
            return "white"
        if result == "0-1":
            return "black"
        return "draw"

    def outcome(self) -> Optional[chess.Outcome]:
        """
        Return python-chess outcome object if game is over.

        Returns:
            chess.Outcome or None.
        """
        return self.board.outcome()

    def move_count(self) -> int:
        """
        Get the number of half-moves played in the game.

        Returns:
            Number of plies in the move stack.
        """
        return len(self.board.move_stack)

    def fullmove_number(self) -> int:
        """
        Get the fullmove number from the board.

        Returns:
            Fullmove number according to FEN.
        """
        return self.board.fullmove_number

    def is_check(self) -> bool:
        """
        Check if the side to move is currently in check.

        Returns:
            True if in check, otherwise False.
        """
        return self.board.is_check()

    def is_checkmate(self) -> bool:
        """
        Check if the game is currently checkmate.

        Returns:
            True if checkmate, otherwise False.
        """
        return self.board.is_checkmate()

    def is_stalemate(self) -> bool:
        """
        Check if the game is currently stalemate.

        Returns:
            True if stalemate, otherwise False.
        """
        return self.board.is_stalemate()

    def is_insufficient_material(self) -> bool:
        """
        Check if the game is drawn by insufficient material.

        Returns:
            True if insufficient material, otherwise False.
        """
        return self.board.is_insufficient_material()

    def is_repetition(self, count: int = 3) -> bool:
        """
        Check if the current position has occurred repeatedly.

        Args:
            count: Repetition count threshold.

        Returns:
            True if repetition condition holds.
        """
        return self.board.is_repetition(count)

    def get_state(self) -> GameState:
        """
        Build a lightweight snapshot of the current game state.

        Returns:
            GameState dataclass instance.
        """
        return GameState(
            fen=self.get_fen(),
            turn=self.current_player(),
            is_terminal=self.is_terminal(),
            result=self.result(),
            legal_moves=self.legal_moves_uci(),
        )

    def __str__(self) -> str:
        """
        Nicely formatted ASCII board representation.
        """
        return str(self.board)
