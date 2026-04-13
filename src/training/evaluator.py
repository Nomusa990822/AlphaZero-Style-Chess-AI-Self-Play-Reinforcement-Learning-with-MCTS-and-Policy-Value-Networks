"""
Evaluation utilities for AlphaZero-style chess training.
"""

from __future__ import annotations

from dataclasses import dataclass

import chess

from src.agents.mcts_agent import MCTSAgent
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.model.inference import ModelInference


@dataclass
class EvaluationResult:
    """
    Evaluation summary from perspective of model A.
    """
    wins: int
    losses: int
    draws: int
    games_played: int

    @property
    def score(self) -> float:
        """
        Score from perspective of agent A:
        win=1, draw=0.5, loss=0
        """
        if self.games_played == 0:
            return 0.0
        return (self.wins + 0.5 * self.draws) / self.games_played


class NetworkEvaluator:
    """
    Lets two networks play head-to-head via MCTS.
    """

    def __init__(
        self,
        move_encoding: MoveEncoding,
        mcts_config: MCTSConfig | None = None,
    ) -> None:
        self.move_encoding = move_encoding
        self.mcts_config = mcts_config or MCTSConfig(
            num_simulations=25,
            add_dirichlet_noise=True,
            dirichlet_alpha=0.3,
            dirichlet_epsilon=0.25,
            temperature=0.2,
        )

    def _play_single_game(
        self,
        agent_white: MCTSAgent,
        agent_black: MCTSAgent,
        max_moves: int = 300,
    ) -> str:
        board = chess.Board()
        move_count = 0

        while not board.is_game_over() and move_count < max_moves:
            move = (
                agent_white.choose_move(
                    board,
                    temperature=self.mcts_config.temperature,
                )
                if board.turn == chess.WHITE
                else agent_black.choose_move(
                    board,
                    temperature=self.mcts_config.temperature,
                )
            )

            board.push(move)
            move_count += 1

        if board.is_game_over():
            return board.result(claim_draw=True)

        # Adjudicate instead of forcing a draw when max_moves is reached.
        _, value = agent_white.inference.predict(board)

        if value > 0.2:
            return "1-0"
        if value < -0.2:
            return "0-1"
        return "1/2-1/2"

    def compare_models(
        self,
        inference_a: ModelInference,
        inference_b: ModelInference,
        num_games: int = 4,
    ) -> EvaluationResult:
        """
        Compare two models head-to-head.
        Model A alternates colors for fairness.
        """
        wins = 0
        losses = 0
        draws = 0

        for game_idx in range(num_games):
            if game_idx % 2 == 0:
                agent_white = MCTSAgent(inference_a, self.move_encoding, self.mcts_config)
                agent_black = MCTSAgent(inference_b, self.move_encoding, self.mcts_config)
                result = self._play_single_game(agent_white, agent_black)

                if result == "1-0":
                    wins += 1
                elif result == "0-1":
                    losses += 1
                else:
                    draws += 1
            else:
                agent_white = MCTSAgent(inference_b, self.move_encoding, self.mcts_config)
                agent_black = MCTSAgent(inference_a, self.move_encoding, self.mcts_config)
                result = self._play_single_game(agent_white, agent_black)

                if result == "1-0":
                    losses += 1
                elif result == "0-1":
                    wins += 1
                else:
                    draws += 1

        return EvaluationResult(
            wins=wins,
            losses=losses,
            draws=draws,
            games_played=num_games,
        )

    def should_promote_candidate(
        self,
        candidate_inference: ModelInference,
        best_inference: ModelInference,
        num_games: int = 6,
        required_score: float = 0.52,
    ) -> tuple[bool, EvaluationResult]:
        """
        Decide whether the candidate model should replace the best model.
        """
        result = self.compare_models(
            inference_a=candidate_inference,
            inference_b=best_inference,
            num_games=num_games,
        )
        return result.score >= required_score, result
