"""
Human player agent for terminal-based chess play.
"""

from __future__ import annotations

import chess


class HumanAgent:
    """
    Human chess player via terminal input.
    """

    def choose_move(self, board: chess.Board) -> chess.Move:
        """
        Prompt the user until a legal move is entered.

        Accepted formats:
        - UCI: e2e4
        - promotion UCI: e7e8q

        Args:
            board: Current chess board

        Returns:
            Legal chess.Move
        """
        legal_uci_moves = {move.uci(): move for move in board.legal_moves}

        while True:
            user_input = input("\nEnter your move in UCI format (e.g. e2e4): ").strip().lower()

            if user_input in {"quit", "exit"}:
                raise KeyboardInterrupt("User exited the game.")

            if user_input in legal_uci_moves:
                return legal_uci_moves[user_input]

            print("Invalid or illegal move. Try again.")
            print(f"Example legal moves: {', '.join(list(legal_uci_moves.keys())[:10])}")
