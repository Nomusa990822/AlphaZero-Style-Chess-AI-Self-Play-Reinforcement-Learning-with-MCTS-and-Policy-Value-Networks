"""Isolated confirmatory paired evaluator; does not alter training promotion logic."""
from __future__ import annotations

import json
import math
import io

import chess.pgn
from pathlib import Path
from typing import Any

import chess

from src.agents.mcts_agent import MCTSAgent
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.training.evaluator import NetworkEvaluator

SUITE_PATH = Path(__file__).resolve().parents[2] / "benchmarks" / "evaluation_openings_confirmatory_v1.jsonl"
DEVELOPMENT_SUITE_PATH = Path(__file__).resolve().parents[2] / "benchmarks" / "evaluation_openings.jsonl"
TACTICAL_SUITE_PATH = Path(__file__).resolve().parents[2] / "benchmarks" / "tactical_positions.jsonl"
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
    tactical = load_tactical_fens(TACTICAL_SUITE_PATH)
    tactical_overlap = fens & tactical
    if tactical_overlap:
        raise ValueError(f"confirmatory suite overlaps tactical corpus at {len(tactical_overlap)} position(s)")
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


def load_tactical_fens(path: str | Path) -> set[str]:
    result: set[str] = set()
    with Path(path).open("r", encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            item = json.loads(raw)
            result.add(_normalized_fen(chess.Board(item["fen"])))
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

    def _play_game(self, agent_white: MCTSAgent, agent_black: MCTSAgent, start: chess.Board, candidate_colour: bool, opening_id: str, leg: str) -> dict[str, Any]:
        board = start.copy(stack=True)
        game = chess.pgn.Game.from_board(board)
        game.headers["Event"] = "Confirmatory paired checkpoint evaluation"
        game.headers["Opening"] = opening_id
        game.headers["Round"] = leg
        game.headers["White"] = "candidate" if candidate_colour == chess.WHITE else "incumbent"
        game.headers["Black"] = "incumbent" if candidate_colour == chess.WHITE else "candidate"
        node = game.end()
        plies = 0
        while not board.is_game_over(claim_draw=True) and plies < MAX_PLIES:
            agent = agent_white if board.turn == chess.WHITE else agent_black
            move = agent.choose_move(board, temperature=0.0)
            if move not in board.legal_moves:
                raise RuntimeError(f"illegal move in {opening_id}/{leg}: {move}")
            board.push(move)
            node = node.add_variation(move)
            plies += 1
        capped = not board.is_game_over(claim_draw=True)
        result = board.result(claim_draw=True) if not capped else "1/2-1/2"
        game.headers["Result"] = result
        game.headers["Termination"] = "move_cap_draw" if capped else "chess_rule"
        candidate_won = result == ("1-0" if candidate_colour == chess.WHITE else "0-1")
        outcome = "draw" if result == "1/2-1/2" else ("win" if candidate_won else "loss")
        return {
            "opening_id": opening_id,
            "leg": leg,
            "starting_fen": start.fen(),
            "result": result,
            "candidate_outcome": outcome,
            "plies": plies,
            "termination": "move_cap_draw" if capped else "chess_rule",
            "uci_moves": [move.uci() for move in board.move_stack[len(start.move_stack):]],
            "pgn": game.accept(chess.pgn.StringExporter(headers=True, variations=False, comments=False)),
        }

    def compare(self, candidate: Any, incumbent: Any) -> dict[str, Any]:
        """Play the complete colour-swapped suite and retain raw game records."""
        candidate_agent = MCTSAgent(candidate, self.engine.move_encoding, self.engine.mcts_config)
        incumbent_agent = MCTSAgent(incumbent, self.engine.move_encoding, self.engine.mcts_config)
        games: list[dict[str, Any]] = []
        pair_scores: list[float] = []
        pair_results: list[dict[str, Any]] = []
        for opening_id, opening_board in self.openings:
            white_game = self._play_game(candidate_agent, incumbent_agent, opening_board, chess.WHITE, opening_id, "candidate_white")
            black_start = opening_board.mirror()
            black_game = self._play_game(incumbent_agent, candidate_agent, black_start, chess.BLACK, opening_id, "candidate_black")
            games.extend((white_game, black_game))
            values = {"win": 1.0, "draw": 0.5, "loss": 0.0}
            pair_score = (values[white_game["candidate_outcome"]] + values[black_game["candidate_outcome"]]) / 2.0
            pair_scores.append(pair_score)
            pair_results.append({
                "opening_id": opening_id,
                "candidate_as_white": white_game["candidate_outcome"],
                "candidate_as_black": black_game["candidate_outcome"],
                "pair_score": pair_score,
            })
        outcomes = [game["candidate_outcome"] for game in games]
        wins, losses, draws = outcomes.count("win"), outcomes.count("loss"), outcomes.count("draw")
        white = [g["candidate_outcome"] for g in games if g["leg"] == "candidate_white"]
        black = [g["candidate_outcome"] for g in games if g["leg"] == "candidate_black"]
        def breakdown(items: list[str]) -> dict[str, int]:
            return {"wins": items.count("win"), "losses": items.count("loss"), "draws": items.count("draw")}
        score = (wins + 0.5 * draws) / GAME_COUNT
        lcb = paired_student_t_lcb90(pair_scores)
        mean = sum(pair_scores) / PAIR_COUNT
        stddev = math.sqrt(sum((x - mean) ** 2 for x in pair_scores) / (PAIR_COUNT - 1))
        return {
            "protocol": "confirmatory_v1",
            "games": GAME_COUNT,
            "opening_pairs": PAIR_COUNT,
            "score": score,
            "pair_score_mean": mean,
            "pair_score_sample_stddev": stddev,
            "one_sided_90_student_t_lcb": lcb,
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "candidate_as_white": breakdown(white),
            "candidate_as_black": breakdown(black),
            "opening_pair_results": pair_results,
            "game_records": games,
            "promotion_evidence_eligible": score > MIN_SCORE and lcb > MIN_SCORE,
            "settings": {"device": "cpu", "mcts_simulations": SIMULATIONS, "dirichlet_noise": False, "temperature": 0.0, "max_plies": MAX_PLIES},
            "limitations": ["fixed curated opening suite", "not an Elo estimate", "not a value-calibration study"],
        }
