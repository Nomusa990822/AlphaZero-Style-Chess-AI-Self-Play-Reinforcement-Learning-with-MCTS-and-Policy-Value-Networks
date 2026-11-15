"""Deterministic, colour-balanced evaluation over distinct mirrored opening pairs."""
from __future__ import annotations
from dataclasses import dataclass
import json
import math
from pathlib import Path
import chess
from src.agents.mcts_agent import MCTSAgent
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.model.inference import ModelInference

MIN_PROMOTION_GAMES = 24
MIN_OPENING_PAIRS = 12
INCUMBENT_SCORE = 0.50
DEFAULT_OPENING_PATH = Path(__file__).resolve().parents[2] / "benchmarks" / "evaluation_openings.jsonl"


def load_evaluation_openings(path: str | Path = DEFAULT_OPENING_PATH) -> list[tuple[str, chess.Board]]:
    """Load and validate the fixed opening suite used for paired evaluation."""
    openings: list[tuple[str, chess.Board]] = []
    seen_ids: set[str] = set()
    seen_fens: set[str] = set()
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                record = json.loads(line)
                opening_id = str(record["id"]).strip()
                moves = record["moves_uci"]
                if not opening_id or not isinstance(moves, list) or not moves:
                    raise ValueError("opening id and non-empty moves_uci are required")
                if opening_id in seen_ids:
                    raise ValueError(f"duplicate opening id {opening_id!r}")
                board = chess.Board()
                for uci in moves:
                    move = chess.Move.from_uci(str(uci))
                    if move not in board.legal_moves:
                        raise ValueError(f"illegal opening move {uci!r}")
                    board.push(move)
                if not board.is_valid() or board.is_game_over(claim_draw=True):
                    raise ValueError("opening must lead to a valid, non-terminal position")
                fen = board.fen()
                if fen in seen_fens:
                    raise ValueError(f"duplicate opening position {opening_id!r}")
                seen_ids.add(opening_id)
                seen_fens.add(fen)
                openings.append((opening_id, board))
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
    if len(openings) < MIN_OPENING_PAIRS:
        raise ValueError(f"Opening suite contains {len(openings)} positions; at least {MIN_OPENING_PAIRS} are required.")
    return openings


@dataclass
class EvaluationResult:
    """Evaluation summary from the perspective of model A (the candidate)."""
    wins: int
    losses: int
    draws: int
    games_played: int
    candidate_white_wins: int = 0
    candidate_white_losses: int = 0
    candidate_white_draws: int = 0
    candidate_black_wins: int = 0
    candidate_black_losses: int = 0
    candidate_black_draws: int = 0
    opening_pair_scores: tuple[float, ...] = ()
    opening_ids: tuple[str, ...] = ()

    @property
    def score(self) -> float:
        if self.games_played == 0:
            return 0.0
        return (self.wins + 0.5 * self.draws) / self.games_played

    @property
    def lower_confidence_bound(self) -> float:
        """One-sided 90% lower bound using independent opening-pair scores."""
        if self.opening_pair_scores:
            scores = self.opening_pair_scores
            n = len(scores)
            if n < 2:
                return 0.0
            mean = sum(scores) / n
            variance = sum((score - mean) ** 2 for score in scores) / (n - 1)
            return max(0.0, mean - 1.645 * math.sqrt(variance / n))
        # Backward-compatible descriptive statistic for legacy result objects.
        n = self.games_played
        if n < 2:
            return 0.0
        mean = self.score
        sum_squares = self.wins + 0.25 * self.draws
        variance = max(0.0, (sum_squares - n * mean * mean) / (n - 1))
        return max(0.0, mean - 1.645 * math.sqrt(variance / n))

    @property
    def colour_breakdown(self) -> dict[str, dict[str, int]]:
        return {
            "candidate_as_white": {"wins": self.candidate_white_wins, "losses": self.candidate_white_losses, "draws": self.candidate_white_draws},
            "candidate_as_black": {"wins": self.candidate_black_wins, "losses": self.candidate_black_losses, "draws": self.candidate_black_draws},
        }


class NetworkEvaluator:
    """Compare two networks on fixed opening positions with mirrored colours."""
    def __init__(
        self,
        move_encoding: MoveEncoding,
        mcts_config: MCTSConfig | None = None,
        opening_positions: list[tuple[str, chess.Board]] | None = None,
    ) -> None:
        self.move_encoding = move_encoding
        self.mcts_config = mcts_config or MCTSConfig(num_simulations=50, add_dirichlet_noise=False, temperature=0.0)
        self.mcts_config.add_dirichlet_noise = False
        self.opening_positions = load_evaluation_openings() if opening_positions is None else opening_positions

    def _play_single_game(
        self,
        agent_white: MCTSAgent,
        agent_black: MCTSAgent,
        max_moves: int = 200,
        starting_board: chess.Board | None = None,
    ) -> str:
        board = starting_board.copy(stack=True) if starting_board is not None else chess.Board()
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
        return "1/2-1/2"

    @staticmethod
    def _candidate_outcome(result: str, candidate_colour: bool) -> str:
        if result == "1/2-1/2":
            return "draw"
        candidate_won = result == ("1-0" if candidate_colour == chess.WHITE else "0-1")
        return "win" if candidate_won else "loss"

    def compare_models(self, inference_a: ModelInference, inference_b: ModelInference, num_games: int = MIN_PROMOTION_GAMES) -> EvaluationResult:
        """Play each opening twice: candidate White, then candidate Black from its mirrored position."""
        if num_games < 2 or num_games % 2 != 0:
            raise ValueError("num_games must be an even number of at least 2 for colour balance.")
        pairs_required = num_games // 2
        if pairs_required > len(self.opening_positions):
            raise ValueError(
                f"Requested {num_games} games but only {len(self.opening_positions)} distinct opening pairs are available."
            )

        wins = losses = draws = 0
        white_wins = white_losses = white_draws = 0
        black_wins = black_losses = black_draws = 0
        pair_scores: list[float] = []
        opening_ids: list[str] = []
        agent_a = MCTSAgent(inference_a, self.move_encoding, self.mcts_config)
        agent_b = MCTSAgent(inference_b, self.move_encoding, self.mcts_config)

        for opening_id, opening_board in self.opening_positions[:pairs_required]:
            opening_ids.append(opening_id)
            white_result = self._play_single_game(agent_a, agent_b, starting_board=opening_board)
            white_outcome = self._candidate_outcome(white_result, chess.WHITE)
            black_result = self._play_single_game(agent_b, agent_a, starting_board=opening_board.mirror())
            black_outcome = self._candidate_outcome(black_result, chess.BLACK)
            pair_score = 0.0

            for outcome, colour in ((white_outcome, chess.WHITE), (black_outcome, chess.BLACK)):
                if outcome == "win":
                    wins += 1
                    pair_score += 1.0
                    if colour == chess.WHITE:
                        white_wins += 1
                    else:
                        black_wins += 1
                elif outcome == "loss":
                    losses += 1
                    if colour == chess.WHITE:
                        white_losses += 1
                    else:
                        black_losses += 1
                else:
                    draws += 1
                    pair_score += 0.5
                    if colour == chess.WHITE:
                        white_draws += 1
                    else:
                        black_draws += 1
            pair_scores.append(pair_score / 2.0)

        return EvaluationResult(
            wins=wins, losses=losses, draws=draws, games_played=num_games,
            candidate_white_wins=white_wins, candidate_white_losses=white_losses, candidate_white_draws=white_draws,
            candidate_black_wins=black_wins, candidate_black_losses=black_losses, candidate_black_draws=black_draws,
            opening_pair_scores=tuple(pair_scores), opening_ids=tuple(opening_ids),
        )

    @staticmethod
    def promotion_rejection_reasons(result: EvaluationResult) -> list[str]:
        reasons: list[str] = []
        if result.games_played < MIN_PROMOTION_GAMES:
            reasons.append(f"only {result.games_played} evaluation games; at least {MIN_PROMOTION_GAMES} are required")
        if len(result.opening_pair_scores) < MIN_OPENING_PAIRS:
            reasons.append(f"only {len(result.opening_pair_scores)} independent opening pairs; at least {MIN_OPENING_PAIRS} are required")
        if result.score <= INCUMBENT_SCORE:
            reasons.append(f"candidate score {result.score:.3f} did not exceed the incumbent baseline of {INCUMBENT_SCORE:.2f}")
        if result.lower_confidence_bound <= INCUMBENT_SCORE:
            reasons.append(f"one-sided 90% lower confidence bound ({result.lower_confidence_bound:.3f}) did not exceed {INCUMBENT_SCORE:.2f}")
        return reasons

    def should_promote_candidate(self, candidate_inference: ModelInference, best_inference: ModelInference, num_games: int = MIN_PROMOTION_GAMES) -> tuple[bool, EvaluationResult]:
        result = self.compare_models(candidate_inference, best_inference, num_games)
        return not self.promotion_rejection_reasons(result), result
