"""Run a finite-depth Stockfish review of selected independent-v2 games.

The script replays every stored UCI move from its recorded starting FEN,
cross-checks SAN from the stored PGN movetext, and compares each played move
with Stockfish's best move at a fixed depth. Results are diagnostic, not Elo
or proof of optimal play.
"""
from __future__ import annotations

import argparse
import io
import json
import shutil
from pathlib import Path
from statistics import mean, median
from typing import Any

import chess
import chess.engine
import chess.pgn

LOSS_IDS = {
    "v2-01-sicilian-taimanov",
    "v2-14-kings-indian",
    "v2-18-english-reversed",
    "v2-21-dutch",
}
DRAW_IDS = {
    "v2-02-sicilian-kan",
    "v2-13-london",
    "v2-17-english-symmetrical",
    "v2-22-pirc",
}
WIN_IDS = {"v2-23-modern"}
EXPECTED_SOURCE_COMMIT = "d84015b8cfe4de536065cbf284d033bbe99e2ca3"
EXPECTED_BASELINE_SHA256 = "7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471"
EXPECTED_CANDIDATE_SHA256 = "101294ee17c79fd9e4816b3e2676b8f87487c4932172861f59b96550c345af00"


def replay_record(record: dict[str, Any]) -> tuple[list[tuple[chess.Board, chess.Move, str]], chess.Board]:
    """Validate the PGN main line from its origin and UCI moves from recorded FEN.

    Evaluation PGNs include opening moves before starting_fen; the UCI list
    starts at that recorded position. Locate the exact FEN in the PGN main
    line before comparing the remaining SAN moves with UCI.
    """
    board = chess.Board(record["starting_fen"])
    moves = record["uci_moves"]
    if len(moves) != record["plies"]:
        raise ValueError(f"{record['opening_id']}: UCI count does not match plies")

    game = chess.pgn.read_game(io.StringIO(record["pgn"]))
    if game is None:
        raise ValueError(f"{record['opening_id']}: PGN could not be parsed")
    if game.errors:
        raise ValueError(f"{record['opening_id']}: PGN parse errors: {game.errors}")
    if game.headers.get("Result") != record.get("result"):
        raise ValueError(f"{record['opening_id']}: PGN result does not match record result")

    pgn_board = game.board()
    mainline = list(game.mainline_moves())
    start_index = None
    for index in range(len(mainline) + 1):
        if pgn_board.fen() == board.fen():
            start_index = index
            break
        if index < len(mainline):
            pgn_board.push(mainline[index])
    if start_index is None:
        raise ValueError(
            f"{record['opening_id']}: recorded starting FEN is not present in PGN main line"
        )

    san_moves = mainline[start_index:]
    if len(san_moves) != len(moves):
        raise ValueError(
            f"{record['opening_id']}: PGN moves after starting FEN {len(san_moves)} "
            f"!= UCI count {len(moves)}"
        )

    positions: list[tuple[chess.Board, chess.Move, str]] = []
    for index, (uci, pgn_move) in enumerate(zip(moves, san_moves), start=1):
        try:
            move = chess.Move.from_uci(uci)
        except ValueError as exc:
            raise ValueError(f"{record['opening_id']} ply {index}: malformed UCI {uci}") from exc
        if move not in board.legal_moves:
            raise ValueError(f"{record['opening_id']} ply {index}: illegal UCI {uci}")
        if pgn_move != move:
            san = board.san(pgn_move)
            raise ValueError(
                f"{record['opening_id']} ply {index}: PGN SAN {san} != UCI {uci}"
            )
        san = board.san(move)
        positions.append((board.copy(stack=False), move, san))
        board.push(move)

    if record.get("result") not in {"1-0", "0-1", "1/2-1/2"}:
        raise ValueError(f"{record['opening_id']}: unsupported result {record.get('result')}")
    if board.is_checkmate() and board.result() != record["result"]:
        raise ValueError(f"{record['opening_id']}: replayed checkmate result mismatch")
    return positions, board


def select_records(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Select all four losses, four predeclared draw controls and the White win."""
    records = [
        record for record in report["game_records"]
        if record.get("leg") == "candidate_white"
    ]
    by_id = {record["opening_id"]: record for record in records}
    selected_ids = LOSS_IDS | DRAW_IDS | WIN_IDS
    missing = selected_ids - by_id.keys()
    if missing:
        raise ValueError(f"missing selected candidate-White games: {sorted(missing)}")
    for opening_id in LOSS_IDS:
        if by_id[opening_id]["candidate_outcome"] != "loss":
            raise ValueError(f"{opening_id} is not a recorded candidate-White loss")
    for opening_id in DRAW_IDS:
        if by_id[opening_id]["candidate_outcome"] != "draw":
            raise ValueError(f"{opening_id} is not a recorded candidate-White draw")
    for opening_id in WIN_IDS:
        if by_id[opening_id]["candidate_outcome"] != "win":
            raise ValueError(f"{opening_id} is not the recorded candidate-White win")
    return [by_id[key] for key in sorted(selected_ids)]


def score_components(info: dict[str, Any], pov: chess.Color) -> tuple[int | None, int | None]:
    """Return centipawns and mate distance separately; never encode mate as CP."""
    score = info["score"].pov(pov)
    return score.score(), score.mate()


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    all_losses = [row["played_move_loss_cp"] for row in rows]
    finite_losses = [value for value in all_losses if value is not None]
    return {
        "moves_analysed": len(rows),
        "moves_with_finite_cp_comparison": len(finite_losses),
        "moves_with_mate_score": len(all_losses) - len(finite_losses),
        "mean_loss_cp_finite_only": round(mean(finite_losses), 1) if finite_losses else None,
        "median_loss_cp_finite_only": round(median(finite_losses), 1) if finite_losses else None,
        "moves_at_least_100cp_finite_only": sum(value >= 100 for value in finite_losses),
        "moves_at_least_200cp_finite_only": sum(value >= 200 for value in finite_losses),
        "largest_finite_loss_cp": max(finite_losses, default=None),
    }


def analyse_game(
    engine: chess.engine.SimpleEngine,
    record: dict[str, Any],
    *,
    depth: int,
) -> dict[str, Any]:
    positions, final_board = replay_record(record)
    move_rows = []
    for ply, (board, played, san) in enumerate(positions, start=1):
        side = board.turn
        best_info = engine.analyse(board, chess.engine.Limit(depth=depth))
        best_pv = best_info.get("pv", [])
        if not best_pv:
            raise RuntimeError(f"{record['opening_id']} ply {ply}: no best PV")
        best_move = best_pv[0]
        best_score_cp, best_score_mate = score_components(best_info, side)
        if played == best_move:
            played_info = best_info
        else:
            played_info = engine.analyse(
                board, chess.engine.Limit(depth=depth), root_moves=[played]
            )
        played_score_cp, played_score_mate = score_components(played_info, side)
        loss_cp = (
            max(0, best_score_cp - played_score_cp)
            if best_score_cp is not None and played_score_cp is not None
            else None
        )
        move_rows.append({
            "ply": ply,
            "side": "white" if side == chess.WHITE else "black",
            "fen": board.fen(),
            "played_san": san,
            "played_uci": played.uci(),
            "best_san": board.san(best_move),
            "best_uci": best_move.uci(),
            "best_score_cp_from_mover_pov": best_score_cp,
            "best_score_mate_from_mover_pov": best_score_mate,
            "played_score_cp_from_mover_pov": played_score_cp,
            "played_score_mate_from_mover_pov": played_score_mate,
            "played_move_loss_cp": loss_cp,
            "best_pv_uci": [move.uci() for move in best_pv[:12]],
            "played_pv_uci": [move.uci() for move in played_info.get("pv", [])[:12]],
        })

    white_rows = [row for row in move_rows if row["side"] == "white"]
    black_rows = [row for row in move_rows if row["side"] == "black"]

    if final_board.fen() == "":
        raise AssertionError("unreachable empty FEN")
    return {
        "opening_id": record["opening_id"],
        "candidate_outcome": record["candidate_outcome"],
        "plies": record["plies"],
        "result": record["result"],
        "termination": record["termination"],
        "final_fen": final_board.fen(),
        "candidate_white_move_summary": summarize_rows(white_rows),
        "incumbent_black_move_summary": summarize_rows(black_rows),
        "moves": move_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-json", type=Path, required=True)
    parser.add_argument("--engine", default="stockfish")
    parser.add_argument("--depth", type=int, default=12)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.depth < 1:
        parser.error("--depth must be positive")

    report = json.loads(args.input_json.read_text(encoding="utf-8"))
    if report.get("source_commit") != EXPECTED_SOURCE_COMMIT:
        raise RuntimeError("source evaluation commit does not match pinned v2 run")
    checkpoints = report.get("checkpoints", {})
    if checkpoints.get("incumbent", {}).get("sha256") != EXPECTED_BASELINE_SHA256:
        raise RuntimeError("incumbent checkpoint digest mismatch")
    if checkpoints.get("candidate", {}).get("sha256") != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError("candidate checkpoint digest mismatch")
    if report.get("opening_suite_sha256") != "69d2582e175bf0a4bfd2867537ea7de4e43f0cfe0a2dfdc5ca6f6d5e0c2fff03":
        raise RuntimeError("opening suite digest mismatch")

    selected = select_records(report)
    engine_path = shutil.which(args.engine) or (args.engine if Path(args.engine).is_file() else None)
    if engine_path is None:
        parser.error(f"Stockfish executable not found: {args.engine}")

    results = []
    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
        engine.configure({"Threads": 1, "Hash": 256})
        engine_name = engine.id.get("name", "unknown")
        engine_author = engine.id.get("author", "unknown")
        for record in selected:
            results.append(analyse_game(engine, record, depth=args.depth))

    outcome_summary = {}
    for outcome in ("loss", "draw", "win"):
        group = [item for item in results if item["candidate_outcome"] == outcome]
        outcome_summary[outcome] = {
            "games": len(group),
            "candidate_white_moves": sum(item["candidate_white_move_summary"]["moves_analysed"] for item in group),
            "candidate_white_moves_with_finite_cp_comparison": sum(item["candidate_white_move_summary"]["moves_with_finite_cp_comparison"] for item in group),
            "candidate_white_moves_with_mate_score": sum(item["candidate_white_move_summary"]["moves_with_mate_score"] for item in group),
            "candidate_white_moves_at_least_100cp_finite_only": sum(item["candidate_white_move_summary"]["moves_at_least_100cp_finite_only"] for item in group),
            "candidate_white_moves_at_least_200cp_finite_only": sum(item["candidate_white_move_summary"]["moves_at_least_200cp_finite_only"] for item in group),
            "mean_candidate_white_move_loss_cp_finite_only": round(mean(
                row["played_move_loss_cp"]
                for item in group
                for row in item["moves"]
                if row["side"] == "white" and row["played_move_loss_cp"] is not None
            ), 1) if any(
                row["side"] == "white" and row["played_move_loss_cp"] is not None
                for item in group for row in item["moves"]
            ) else None,
        }

    output = {
        "schema_version": 2,
        "source": {
            "workflow_run_id": 43759687103,
            "artifact_id": 14180972985,
            "source_commit": EXPECTED_SOURCE_COMMIT,
            "opening_suite_sha256": report["opening_suite_sha256"],
            "baseline_sha256": EXPECTED_BASELINE_SHA256,
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
        },
        "engine": {"name": engine_name, "author": engine_author},
        "configuration": {"depth": args.depth, "threads": 1, "hash_mb": 256},
        "selection": {
            "losses": sorted(LOSS_IDS),
            "draw_controls": sorted(DRAW_IDS),
            "white_win": sorted(WIN_IDS),
            "selection_rationale": "Four losses plus four predeclared draws selected to span related opening families and game lengths, and the sole candidate-White win.",
        },
        "summary_by_outcome": outcome_summary,
        "limitations": [
            "Finite-depth Stockfish scores depend on engine version, depth and hardware; they are diagnostic, not a proof of best play.",
            "The four losses and selected controls are a small, deliberately selected sample, not a representative statistical sample.",
            "Centipawn loss is measured at fixed depth from the side-to-move perspective before each played move. Positions with a mate score are reported separately and excluded from finite centipawn-loss aggregates; mate distance is not centipawn loss.",
            "The baseline's moves are included as opponent context; this does not compare the two checkpoints in a new match or estimate Elo.",
            "No training, optimizer update, checkpoint write or promotion is performed.",
        ],
        "games": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"engine": output["engine"], "configuration": output["configuration"], "summary_by_outcome": outcome_summary}, indent=2))
    print(f"Full move-by-move report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
