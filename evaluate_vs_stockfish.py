"""Run colour-balanced matches between saved networks and fixed Stockfish Elo levels.

This is a playing-strength experiment, not a training workflow. It never writes
or promotes checkpoints. Each model plays both colours from the same six
predefined opening positions against each configured Stockfish Elo setting.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import chess
import chess.engine
import torch

from src.agents.mcts_agent import MCTSAgent
from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import load_checkpoint


OPENING_LINES: tuple[tuple[str, ...], ...] = (
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5"),
    ("e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4"),
    ("e2e4", "e7e6", "d2d4", "d7d5", "b1c3", "g8f6"),
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6"),
    ("e2e4", "c7c6", "d2d4", "d7d5", "b1c3", "d5e4"),
    ("c2c4", "e7e5", "b1c3", "g8f6", "g2g3", "d7d5"),
)
DEFAULT_ELO_LEVELS = (1320, 1600, 1900)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, help="Random-initialisation baseline checkpoint.")
    parser.add_argument("--candidate", required=True, help="One-iteration pilot candidate checkpoint.")
    parser.add_argument("--stockfish", default="stockfish", help="Stockfish executable.")
    parser.add_argument("--elo-levels", nargs="+", type=int, default=list(DEFAULT_ELO_LEVELS))
    parser.add_argument("--games-per-level", type=int, default=12,
                        help="Games per checkpoint and Elo; must be a multiple of 12 for six openings and both colours.")
    parser.add_argument("--simulations", type=int, default=16)
    parser.add_argument("--max-plies", type=int, default=120)
    parser.add_argument("--stockfish-move-time", type=float, default=0.05)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.games_per_level < len(OPENING_LINES) * 2 or args.games_per_level % (len(OPENING_LINES) * 2):
        parser.error("--games-per-level must be a positive multiple of 12 (six openings, both colours).")
    if args.simulations < 1 or args.max_plies < 2 or args.stockfish_move_time <= 0:
        parser.error("simulations, max plies and Stockfish move time must be positive.")
    if not args.elo_levels or any(level < 1320 or level > 3190 for level in args.elo_levels):
        parser.error("Stockfish Elo levels must be between 1320 and 3190.")
    if len(set(args.elo_levels)) != len(args.elo_levels):
        parser.error("Stockfish Elo levels must be unique.")
    return args


def build_opening_board(line: tuple[str, ...]) -> chess.Board:
    board = chess.Board()
    for uci in line:
        move = chess.Move.from_uci(uci)
        if move not in board.legal_moves:
            raise ValueError(f"Illegal move {uci} in fixed opening line.")
        board.push(move)
    if board.turn != chess.WHITE:
        raise ValueError("Opening lines must leave White to move for paired colour swaps.")
    return board


def build_match_schedule(games_per_level: int) -> list[dict[str, Any]]:
    """Return balanced opening/colour pairs in deterministic order."""
    pair_repeats = games_per_level // (len(OPENING_LINES) * 2)
    schedule: list[dict[str, Any]] = []
    for repeat in range(pair_repeats):
        for opening_index in range(len(OPENING_LINES)):
            schedule.append({"opening_index": opening_index, "model_color": "white", "repeat": repeat})
            schedule.append({"opening_index": opening_index, "model_color": "black", "repeat": repeat})
    return schedule


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_agent(checkpoint_path: Path, simulations: int) -> tuple[MCTSAgent, dict[str, Any]]:
    encoding = MoveEncoding()
    network = AlphaZeroNet(
        action_size=encoding.action_size,
        config=NetworkConfig(
            input_channels=20,
            board_size=8,
            num_filters=64,
            num_res_blocks=3,
            value_hidden_size=128,
        ),
    )
    payload = load_checkpoint(checkpoint_path, network, optimizer=None, map_location="cpu")
    network.eval()
    inference = ModelInference(network, encoding, BoardEncoder(), device="cpu")
    agent = MCTSAgent(
        inference,
        encoding,
        MCTSConfig(
            num_simulations=simulations,
            add_dirichlet_noise=False,
            temperature=0.0,
            use_tactical_root_filter=True,
            use_static_exchange_ordering=True,
        ),
    )
    metadata = {
        "path": checkpoint_path.name,
        "size_bytes": checkpoint_path.stat().st_size,
        "sha256": sha256_file(checkpoint_path),
        "epoch": payload.get("epoch"),
        "extra": payload.get("extra", {}),
    }
    return agent, metadata


def play_game(
    board: chess.Board,
    model_agent: MCTSAgent,
    engine: chess.engine.SimpleEngine,
    model_color: chess.Color,
    max_plies: int,
    move_time: float,
) -> dict[str, Any]:
    start_fen = board.fen()
    while not board.is_game_over(claim_draw=True) and board.ply() < max_plies:
        if board.turn == model_color:
            move = model_agent.choose_move(board, temperature=0.0)
            if move not in board.legal_moves:
                raise RuntimeError(f"Model returned illegal move {move} from {board.fen()}")
        else:
            response = engine.play(board, chess.engine.Limit(time=move_time))
            move = response.move
            if move is None or move not in board.legal_moves:
                raise RuntimeError(f"Stockfish returned an invalid move from {board.fen()}")
        board.push(move)

    result = board.result(claim_draw=True) if board.is_game_over(claim_draw=True) else "1/2-1/2"
    if result == "1-0":
        model_result = "win" if model_color == chess.WHITE else "loss"
    elif result == "0-1":
        model_result = "win" if model_color == chess.BLACK else "loss"
    else:
        model_result = "draw"
    return {
        "starting_fen": start_fen,
        "model_color": "white" if model_color == chess.WHITE else "black",
        "result": result,
        "model_result": model_result,
        "plies": board.ply(),
        "termination": board.outcome(claim_draw=True).termination.name
            if board.is_game_over(claim_draw=True) else "move_limit_draw",
    }


def summarise(games: list[dict[str, Any]]) -> dict[str, Any]:
    wins = sum(game["model_result"] == "win" for game in games)
    losses = sum(game["model_result"] == "loss" for game in games)
    draws = sum(game["model_result"] == "draw" for game in games)
    n = len(games)
    return {
        "games": n,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "score": (wins + 0.5 * draws) / n if n else 0.0,
        "white": {
            "games": sum(g["model_color"] == "white" for g in games),
            "wins": sum(g["model_color"] == "white" and g["model_result"] == "win" for g in games),
            "draws": sum(g["model_color"] == "white" and g["model_result"] == "draw" for g in games),
            "losses": sum(g["model_color"] == "white" and g["model_result"] == "loss" for g in games),
        },
        "black": {
            "games": sum(g["model_color"] == "black" for g in games),
            "wins": sum(g["model_color"] == "black" and g["model_result"] == "win" for g in games),
            "draws": sum(g["model_color"] == "black" and g["model_result"] == "draw" for g in games),
            "losses": sum(g["model_color"] == "black" and g["model_result"] == "loss" for g in games),
        },
        "average_plies": sum(g["plies"] for g in games) / n if n else 0.0,
    }


def run_evaluation(args: argparse.Namespace) -> dict[str, Any]:
    baseline_path = Path(args.baseline)
    candidate_path = Path(args.candidate)
    for path in (baseline_path, candidate_path):
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Checkpoint missing or empty: {path}")

    baseline_agent, baseline_meta = load_agent(baseline_path, args.simulations)
    candidate_agent, candidate_meta = load_agent(candidate_path, args.simulations)
    models = {
        "baseline_random_initialisation": (baseline_agent, baseline_meta),
        "candidate_after_one_pilot_iteration": (candidate_agent, candidate_meta),
    }
    schedule = build_match_schedule(args.games_per_level)
    engine = chess.engine.SimpleEngine.popen_uci(args.stockfish)
    try:
        engine.configure({"Threads": 1, "Hash": 64})
        engine_version = engine.id.get("name", "unknown")
        option_names = engine.options
        if "UCI_LimitStrength" not in option_names or "UCI_Elo" not in option_names:
            raise RuntimeError("Stockfish must support UCI_LimitStrength and UCI_Elo options.")
        reports: dict[str, Any] = {}
        for model_name, (agent, metadata) in models.items():
            by_elo: dict[str, Any] = {}
            for elo in args.elo_levels:
                engine.configure({"UCI_LimitStrength": True, "UCI_Elo": elo})
                games: list[dict[str, Any]] = []
                for item in schedule:
                    board = build_opening_board(OPENING_LINES[item["opening_index"]])
                    model_color = chess.WHITE if item["model_color"] == "white" else chess.BLACK
                    game = play_game(
                        board, agent, engine, model_color,
                        max_plies=args.max_plies,
                        move_time=args.stockfish_move_time,
                    )
                    game.update({
                        "opening_index": item["opening_index"],
                        "opening_moves_uci": list(OPENING_LINES[item["opening_index"]]),
                        "repeat": item["repeat"],
                    })
                    games.append(game)
                by_elo[str(elo)] = {**summarise(games), "games_detail": games}
            reports[model_name] = {"checkpoint": metadata, "by_stockfish_elo": by_elo}
    finally:
        engine.quit()

    return {
        "schema_version": 1,
        "evaluation": "colour_balanced_fixed_stockfish_opponents",
        "stockfish": {
            "name": engine_version,
            "strength_control": "UCI_LimitStrength=true; UCI_Elo per group",
            "elo_levels": args.elo_levels,
            "threads": 1,
            "hash_mb": 64,
            "move_time_seconds": args.stockfish_move_time,
        },
        "model_search": {
            "mcts_simulations": args.simulations,
            "dirichlet_noise": False,
            "temperature": 0.0,
            "tactical_root_filter": True,
            "static_exchange_ordering": True,
            "device": "cpu",
        },
        "design": {
            "games_per_checkpoint_per_elo": args.games_per_level,
            "total_games": len(models) * len(args.elo_levels) * args.games_per_level,
            "max_plies": args.max_plies,
            "opening_positions": len(OPENING_LINES),
            "colour_balance": "exactly half White and half Black for every checkpoint/Elo group",
            "paired_openings": "each opening is played once with the model as White and once as Black",
        },
        "models": reports,
        "limitations": [
            "The checkpoints are a random-initialisation baseline and a candidate after only one tiny pilot iteration; neither is established as a trained strong model.",
            "A small match sample is noisy and must not be converted into an Elo claim.",
            "Stockfish UCI_Elo is a controlled engine setting, not a perfectly calibrated human rating.",
            "Results apply only to this engine version, configuration, opening set, search budget and time control.",
        ],
    }


def main() -> None:
    args = parse_args()
    report = run_evaluation(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"Saved match report: {output}")


if __name__ == "__main__":
    main()
