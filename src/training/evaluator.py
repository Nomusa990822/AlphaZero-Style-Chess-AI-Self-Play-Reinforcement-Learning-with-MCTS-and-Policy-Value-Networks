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
            temperature=0.5,
        )

    @staticmethod
    def _value_to_white_perspective(board: chess.Board, side_to_move_value: float) -> float:
        """
        Convert model value from side-to-move perspective to White perspective.
        """
        return side_to_move_value if board.turn == chess.WHITE else -side_to_move_value

    @staticmethod
    def _material_score_white(board: chess.Board) -> int:
        """
        Simple material score from White perspective.
        """
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0,
        }

        score = 0
        for piece_type, value in piece_values.items():
            score += len(board.pieces(piece_type, chess.WHITE)) * value
            score -= len(board.pieces(piece_type, chess.BLACK)) * value
        return score

    def _adjudicate_result(
        self,
        board: chess.Board,
        inference: ModelInference,
        value_threshold: float = 0.15,
        material_threshold: int = 3,
    ) -> str:
        """
        Decide result for non-terminal positions using both model value and material.
        """
        _, side_to_move_value = inference.predict(board)
        white_value = self._value_to_white_perspective(board, side_to_move_value)
        material_score = self._material_score_white(board)

        if white_value >= value_threshold and material_score >= material_threshold:
            return "1-0"
        if white_value <= -value_threshold and material_score <= -material_threshold:
            return "0-1"
        return "1/2-1/2"

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
                agent_white.choose_move(board, temperature=self.mcts_config.temperature)
                if board.turn == chess.WHITE
                else agent_black.choose_move(board, temperature=self.mcts_config.temperature)
            )
            board.push(move)
            move_count += 1

        if board.is_game_over():
            return board.result(claim_draw=True)

        return self._adjudicate_result(board, agent_white.inference)

    def compare_models(
        self,
        inference_a: ModelInference,
        inference_b: ModelInference,
        num_games: int = 10,
    ) -> EvaluationResult:
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
        num_games: int = 10,
        required_score: float = 0.52,
    ) -> tuple[bool, EvaluationResult]:
        result = self.compare_models(
            inference_a=candidate_inference,
            inference_b=best_inference,
            num_games=num_games,
        )
        return result.score >= required_score, result
