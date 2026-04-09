"""
Agent wrapper around AlphaZero-style MCTS.
"""

from __future__ import annotations

import chess

from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTS, MCTSConfig
from src.model.inference import ModelInference


class MCTSAgent:
    """
    Chess agent that selects moves using MCTS.
    """

    def __init__(
        self,
        inference: ModelInference,
        move_encoding: MoveEncoding,
        mcts_config: MCTSConfig | None = None,
    ) -> None:
        self.inference = inference
        self.move_encoding = move_encoding
        self.mcts = MCTS(
            inference=inference,
            move_encoding=move_encoding,
            config=mcts_config or MCTSConfig(),
        )

    def choose_move(self, board: chess.Board, temperature: float | None = None) -> chess.Move:
        """
        Run MCTS and choose a move.

        Args:
            board: Current board
            temperature: Optional selection temperature

        Returns:
            Selected move
        """
        root = self.mcts.run(board)
        return self.mcts.select_action(root, temperature=temperature)
