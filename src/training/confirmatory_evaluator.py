"""Isolated confirmatory paired evaluator; does not alter training promotion logic."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import chess

from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.training.evaluator import NetworkEvaluator

SUITE_PATH = Path(__file__).resolve().parents[2] / "benchmarks" / "evaluation_openings_confirmatory_v1.jsonl"
DEVELOPMENT_SUITE_PATH = Path(__file__).resolve().parents[2] / "benchmarks" / "evaluation_openings.jsonl"
PAIR_COUNT = 24
GAME_COUNT = 48
SIMULATIONS = 50
MAX_PLIES = 200
# Student-t 90th percentile, df=23 (verified against scipy.stats.t.ppf(0.90, 23)).
T_ONE_SIDED_90_DF23 = 1.319460
MIN_SCORE = 0.50


def _normalized_fen(board: chess.Board) -> str:
    return board.fen(en_passant="fen")


def load_confirmatory_openings(path: str | Path = SUITE_PATH) -> list[tuple[str, chess.Board]]:
    """Load exactly 24 legal, unique, non-terminal positions with family constraints."""
    records: list[tuple[str, chess.Board]] = []
    ids: set[str] = set()
    fens: set[str] = set()
    families: dict[str, int] = {}
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, 1):
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            try:
                item = json.loads(raw)
                opening_id = str(item["id"]).strip()
                family = str(item["family"]).strip()
                moves = item["moves_uci"]
                if item.get("suite_version") != "confirmatory_v1":
                    raise ValueError("suite_version must be confirmatory_v1")
                if not opening_id or not family or not isinstance(moves, list) or not moves:
                    raise ValueError("id, family and non-empty moves_uci are required")
                if opening_id in ids:
                    raise ValueError(f"duplicate opening id: {opening_id}")
                board = chess.Board()
                for uci in moves:
                    move = chess.Move.from_uci(str(uci))
                    if move not in board.legal_moves:
                        raise ValueError(f"illegal move {uci}")
                    board.push(move)
                if not board.is_valid() or board.is_game_over(claim_draw=True):
                    raise ValueError("opening position must be valid and non-terminal")
                fen = _normalized_fen(board)
                if fen in fens:
                    raise ValueError("duplicate normalized opening position")
                ids.add(opening_id)
                fens.add(fen)
                families[family] = families.get(family, 0) + 1
                if families[family] > 4:
                    raise ValueError(f"opening family {family!r} exceeds four positions")
                records.append((opening_id, board))
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"{path}:{line_no}: {exc}") from exc
    if len(records) != PAIR_COUNT:
        raise ValueError(f"confirmatory suite must contain exactly {PAIR_COUNT} positions; found {len(records)}")
    if len(families) < 8:
        raise ValueError(f"confirmatory suite must cover at least 8 families; found {len(families)}")

    development = load_development_fens(DEVELOPMENT_SUITE_PATH)
    overlap = fens & development
    if overlap:
        raise ValueError(f"confirmatory suite overlaps development suite at {len(overlap)} position(s)")
    return records


def load_development_fens(path: str | Path) -> set[str]:
    result: set[str] = set()
    with Path(path).open("r", encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            item = json.loads(raw)
            board = chess.Board()
            for uci in item["moves_uci"]:
                board.push_uci(uci)
            result.add(_normalized_fen(board))
    return result


def paired_student_t_lcb90(pair_scores: tuple[float, ...] | list[float]) -> float:
    """One-sided 90% Student-t lower bound for exactly 24 independent pair scores."""
    if len(pair_scores) != PAIR_COUNT:
        raise ValueError(f"exactly {PAIR_COUNT} paired scores are required")
    if any(not math.isfinite(x) or not 0.0 <= x <= 1.0 for x in pair_scores):
        raise ValueError("pair scores must be finite values in [0, 1]")
    mean = sum(pair_scores) / PAIR_COUNT
    variance = sum((x - mean) ** 2 for x in pair_scores) / (PAIR_COUNT - 1)
    return mean - T_ONE_SIDED_90_DF23 * math.sqrt(variance / PAIR_COUNT)


class ConfirmatoryPairedEvaluator:
    """Runs 24 colour-swapped pairs through the existing inference-only match engine."""

    def __init__(self, move_encoding: MoveEncoding | None = None) -> None:
        self.openings = load_confirmatory_openings()
        config = MCTSConfig(
            num_simulations=SIMULATIONS,
            add_dirichlet_noise=False,
            temperature=0.0,
        )
        self.engine = NetworkEvaluator(
            move_encoding=move_encoding or MoveEncoding(),
            mcts_config=config,
            opening_positions=self.openings,
        )

    def compare(self, candidate: Any, incumbent: Any) -> dict[str, Any]:
        result = self.engine.compare_models(candidate, incumbent, num_games=GAME_COUNT)
        if len(result.opening_pair_scores) != PAIR_COUNT or result.games_played != GAME_COUNT:
            raise RuntimeError("incomplete confirmatory evaluation; all 24 pairs and 48 games are mandatory")
        pair_scores = tuple(result.opening_pair_scores)
        lcb = paired_student_t_lcb90(pair_scores)
        white = result.candidate_white_wins + 0.5 * result.candidate_white_draws
        black = result.candidate_black_wins + 0.5 * result.candidate_black_draws
        return {
            "protocol": "confirmatory_v1",
            "games": GAME_COUNT,
            "opening_pairs": PAIR_COUNT,
            "score": result.score,
            "pair_score_mean": sum(pair_scores) / PAIR_COUNT,
            "pair_score_sample_stddev": math.sqrt(sum((x - sum(pair_scores)/PAIR_COUNT) ** 2 for x in pair_scores) / (PAIR_COUNT - 1)),
            "one_sided_90_student_t_lcb": lcb,
            "wins": result.wins,
            "losses": result.losses,
            "draws": result.draws,
            "candidate_as_white": result.colour_breakdown["candidate_as_white"],
            "candidate_as_black": result.colour_breakdown["candidate_as_black"],
            "opening_pair_results": list(result.opening_pair_results),
            "promotion_evidence_eligible": result.score > MIN_SCORE and lcb > MIN_SCORE,
            "settings": {"device": "cpu", "mcts_simulations": SIMULATIONS, "dirichlet_noise": False, "temperature": 0.0, "max_plies": MAX_PLIES},
            "limitations": ["fixed curated opening suite", "not an Elo estimate", "not a value-calibration study"],
        }
