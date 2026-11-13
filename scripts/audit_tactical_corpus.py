"""Run a reproducible Stockfish review of curated tactical positions.

This is an advisory audit: engine evaluations depend on version, depth and hardware.
It does not automatically validate a human motif annotation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
from typing import Any

import chess
import chess.engine

from src.training.tactical_benchmark import load_tactical_positions


MATE_SCORE = 100_000


def score_cp(info: dict[str, Any], turn: chess.Color) -> int:
    score = info["score"].pov(turn).score(mate_score=MATE_SCORE)
    if score is None:
        raise ValueError("Engine returned an unscorable result.")
    return int(score)


def pv_uci(board: chess.Board, pv: list[chess.Move]) -> list[str]:
    return [move.uci() for move in pv]


def audit_position(
    engine: chess.engine.SimpleEngine,
    case: Any,
    *,
    depth: int,
    multipv: int,
    max_loss_cp: int,
) -> dict[str, Any]:
    board = chess.Board(case.fen)
    top_lines = engine.analyse(board, chess.engine.Limit(depth=depth), multipv=multipv)
    if isinstance(top_lines, dict):
        top_lines = [top_lines]
    if not top_lines:
        raise RuntimeError(f"Stockfish returned no principal variation for {case.position_id}.")

    best_score = score_cp(top_lines[0], board.turn)
    best_moves = [
        line["pv"][0].uci()
        for line in top_lines
        if line.get("pv")
    ]
    lines = [
        {
            "rank": rank,
            "move": line["pv"][0].uci(),
            "score_cp": score_cp(line, board.turn),
            "principal_variation_uci": pv_uci(board, line.get("pv", [])),
        }
        for rank, line in enumerate(top_lines, start=1)
        if line.get("pv")
    ]

    accepted = []
    for move_uci in sorted(case.acceptable_moves):
        move = chess.Move.from_uci(move_uci)
        info = engine.analyse(
            board,
            chess.engine.Limit(depth=depth),
            root_moves=[move],
        )
        move_score = score_cp(info, board.turn)
        loss = best_score - move_score
        accepted.append({
            "move": move_uci,
            "score_cp": move_score,
            "loss_from_engine_best_cp": loss,
            "within_tolerance": loss <= max_loss_cp,
            "principal_variation_uci": pv_uci(board, info.get("pv", [])),
        })

    accepted_within_tolerance = [
        item["move"] for item in accepted if item["within_tolerance"]
    ]
    return {
        "id": case.position_id,
        "motif": case.motif,
        "phase": case.phase,
        "side_to_move": "white" if board.turn == chess.WHITE else "black",
        "fen": case.fen,
        "human_acceptable_moves": sorted(case.acceptable_moves),
        "engine_best_score_cp": best_score,
        "engine_top_lines": lines,
        "accepted_move_analysis": accepted,
        "accepted_move_within_tolerance": accepted_within_tolerance,
        "review_status": (
            "engine_supports_at_least_one_accepted_move"
            if accepted_within_tolerance
            else "human_review_required_engine_disagrees"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--positions", type=Path, default=Path("benchmarks/tactical_positions.jsonl"))
    parser.add_argument("--engine", default="stockfish", help="Stockfish executable path")
    parser.add_argument("--depth", type=int, default=18)
    parser.add_argument("--multipv", type=int, default=5)
    parser.add_argument("--max-loss-cp", type=int, default=150)
    parser.add_argument("--output", type=Path, default=Path("reports/tactical-engine-audit.json"))
    args = parser.parse_args()

    if args.depth < 1 or args.multipv < 1 or args.max_loss_cp < 0:
        parser.error("--depth and --multipv must be positive; --max-loss-cp cannot be negative.")
    engine_path = shutil.which(args.engine) or (args.engine if Path(args.engine).is_file() else None)
    if engine_path is None:
        parser.error(f"Stockfish executable not found: {args.engine}")

    positions = load_tactical_positions(args.positions)
    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
        engine.configure({"Threads": 1, "Hash": 256})
        engine_name = engine.id.get("name", "unknown")
        engine_author = engine.id.get("author", "unknown")
        results = [
            audit_position(
                engine,
                case,
                depth=args.depth,
                multipv=args.multipv,
                max_loss_cp=args.max_loss_cp,
            )
            for case in positions
        ]

    flagged = sum(item["review_status"] != "engine_supports_at_least_one_accepted_move" for item in results)
    report = {
        "schema_version": 1,
        "engine": {"name": engine_name, "author": engine_author},
        "configuration": {
            "depth": args.depth,
            "multipv": args.multipv,
            "max_loss_cp": args.max_loss_cp,
            "threads": 1,
            "hash_mb": 256,
        },
        "summary": {
            "positions": len(results),
            "supported_positions": len(results) - flagged,
            "flagged_for_human_review": flagged,
        },
        "limitations": [
            "This is a finite-depth engine review, not a proof of tactical correctness.",
            "Engine support does not validate the human motif label or prove the move is uniquely best.",
            "Review flagged positions and annotations manually before treating them as benchmark ground truth.",
        ],
        "positions": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Report written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
