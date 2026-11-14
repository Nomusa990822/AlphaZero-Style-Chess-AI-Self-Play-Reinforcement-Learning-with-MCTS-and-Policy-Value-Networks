"""
Deterministic, colour-balanced evaluation for AlphaZero-style chess training.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import chess

from src.agents.mcts_agent import MCTSAgent
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.model.inference import ModelInference


# Promotion is deliberately evidence-based. A 24-game minimum prevents the
# two-game smoke pilot from ever replacing a champion, even with a perfect score.
MIN_PROMOTION_GAMES = 24
INCUMBENT_SCORE = 0.50


@dataclass
class EvaluationResult:
    """Evaluation summary from the perspective of model A."""

    wins: int
    losses: int
    draws: int
    games_played: int

    @property
    def score(self) -> float:
        """Score from model A's perspective: win=1, draw=0.5, loss=0."""
        if self.games_played == 0:
            return 0.0
        return (self.wins + 0.5 * self.draws) / self.games_played

    @property
    def lower_confidence_bound(self) -> float:
        """Approximate one-sided 90% lower confidence bound for match score."""
        n = self.games_played
        if n < 2:
            return 0.0
        mean = self.score
        sum_squares = self.wins + 0.25 * self.draws
        sample_variance = max(0.0, (sum_squares - n * mean * mean) / (n - 1))
        standard_error = math.sqrt(sample_variance / n)
        return max(0.0, mean - 1.645 * standard_error)


class NetworkEvaluator:
    """Compare two networks using deterministic MCTS and swapped colours."""

    def __init__(
        self,
        move_encoding: MoveEncoding,
        mcts_config: MCTSConfig | None = None,
    ) -> None:
        self.move_encoding = move_encoding
        self.mcts_config = mcts_config or MCTSConfig(
            num_simulations=50,
            add_dirichlet_noise=False,
            temperature=0.0,
        )
        # Evaluation must not inject exploration noise.
        self.mcts_config.add_dirichlet_noise = False

    def _play_single_game(
        self,
        agent_white: MCTSAgent,
        agent_black: MCTSAgent,
        max_moves: int = 200,
    ) -> str:
        board = chess.Board()
        move_count = 0

        while not board.is_game_over(claim_draw=True) and move_count < max_moves:
            agent = agent_white if board.turn == chess.WHITE else agent_black
            move = agent.choose_move(board, temperature=0.0)
            if move not in board.legal_moves:
                raise RuntimeError(f"Evaluator agent returned illegal move: {move}")
            board.push(move)
            move_count += 1

        if board.is_game_over(claim_draw=True):
            return board.result(claim_draw=True)

        # A move-limit result is a draw. Material-only adjudication is too
        # crude and can systematically reward a candidate for material grabs.
        return "1/2-1/2"

    def compare_models(
        self,
        inference_a: ModelInference,
        inference_b: ModelInference,
        num_games: int = 12,
    ) -> EvaluationResult:
        """Compare models with alternating colours in paired game order."""
        if num_games < 2 or num_games % 2 != 0:
            raise ValueError("num_games must be an even number of at least 2 for colour balance.")

        wins = losses = draws = 0
        agent_a = MCTSAgent(inference_a, self.move_encoding, self.mcts_config)
        agent_b = MCTSAgent(inference_b, self.move_encoding, self.mcts_config)

        for game_idx in range(num_games):
            if game_idx % 2 == 0:
                result = self._play_single_game(agent_a, agent_b)
                model_a_result = result
            else:
                result = self._play_single_game(agent_b, agent_a)
                model_a_result = "0-1" if result == "1-0" else "1-0" if result == "0-1" else result

            if model_a_result == "1-0":
                wins += 1
            elif model_a_result == "0-1":
                losses += 1
            else:
                draws += 1

        return EvaluationResult(wins, losses, draws, num_games)

    @staticmethod
    def promotion_rejection_reasons(result: EvaluationResult) -> list[str]:
        """Explain which incumbent-relative promotion requirements were not met."""
        reasons: list[str] = []
        if result.games_played < MIN_PROMOTION_GAMES:
            reasons.append(
                f"only {result.games_played} evaluation games; "
                f"at least {MIN_PROMOTION_GAMES} are required"
            )
        if result.score <= INCUMBENT_SCORE:
            reasons.append(
                f"candidate score {result.score:.3f} did not exceed the "
                f"incumbent baseline of {INCUMBENT_SCORE:.2f}"
            )
        if result.lower_confidence_bound <= INCUMBENT_SCORE:
            reasons.append(
                f"one-sided 90% lower confidence bound "
                f"({result.lower_confidence_bound:.3f}) did not exceed "
                f"{INCUMBENT_SCORE:.2f}"
            )
        return reasons

    def should_promote_candidate(
        self,
        candidate_inference: ModelInference,
        best_inference: ModelInference,
        num_games: int = 24,
    ) -> tuple[bool, EvaluationResult]:
        """Promote only on a sufficiently sampled, statistically supported win over the incumbent."""
        result = self.compare_models(candidate_inference, best_inference, num_games)
        promoted = not self.promotion_rejection_reasons(result)
        return promoted, result
