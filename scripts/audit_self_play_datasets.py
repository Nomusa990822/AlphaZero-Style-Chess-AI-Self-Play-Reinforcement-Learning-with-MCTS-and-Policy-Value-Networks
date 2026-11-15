"""Read-only comparison of two archived self-play datasets.

The inputs are JSONL files emitted by MetricsLogger. No model is loaded and
no checkpoint, replay buffer, or source dataset is modified.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import chess
import chess.pgn


def _expected_target(result: str, turn: bool) -> float:
    white_value = 1.0 if result == "1-0" else -1.0 if result == "0-1" else 0.0
    return white_value if turn == chess.WHITE else -white_value


def audit_dataset(path: str | Path, label: str) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"{label} dataset does not exist: {source}")

    outcomes: Counter[str] = Counter()
    terminations: Counter[str] = Counter()
    side_counts: Counter[str] = Counter()
    target_counts: Counter[str] = Counter()
    target_sums: defaultdict[str, float] = defaultdict(float)
    games = 0
    positions = 0
    errors: list[str] = []

    with source.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                record = json.loads(raw)
                result = record["result"]
                pgn_text = record["pgn"]
                targets = record.get("position_targets")
                if result not in {"1-0", "0-1", "1/2-1/2"}:
                    raise ValueError(f"unsupported game result {result!r}")
                if not isinstance(targets, list):
                    raise ValueError("missing position_targets; this is a legacy PGN-only record")

                import io
                game = chess.pgn.read_game(io.StringIO(pgn_text))
                if game is None:
                    raise ValueError("PGN could not be parsed")
                if game.headers.get("Result") != result:
                    raise ValueError("PGN result does not match JSON result")
                moves = list(game.mainline_moves())
                if len(moves) != record["move_count"] or len(targets) != len(moves):
                    raise ValueError("move, sample, and target counts do not agree")

                board = game.board()
                for ply, (move, target_record) in enumerate(zip(moves, targets)):
                    if move not in board.legal_moves:
                        raise ValueError(f"illegal PGN move at ply {ply}")
                    if target_record.get("ply") != ply:
                        raise ValueError(f"unexpected target ply index at ply {ply}")
                    if target_record.get("fen") != board.fen():
                        raise ValueError(f"FEN mismatch at ply {ply}")
                    side = "white" if board.turn == chess.WHITE else "black"
                    if target_record.get("side_to_move") != side:
                        raise ValueError(f"side-to-move mismatch at ply {ply}")
                    target = float(target_record["value_target"])
                    expected = _expected_target(result, board.turn)
                    if abs(target - expected) > 1e-7:
                        raise ValueError(
                            f"value target mismatch at ply {ply}: expected {expected}, got {target}"
                        )
                    side_counts[side] += 1
                    target_counts[str(target)] += 1
                    target_sums[side] += target
                    positions += 1
                    board.push(move)

                games += 1
                outcomes[result] += 1
                terminations[str(record.get("termination", "unknown"))] += 1
            except Exception as exc:
                errors.append(f"line {line_number}: {exc}")

    side_summary = {}
    for side in ("white", "black"):
        count = side_counts[side]
        side_summary[side] = {
            "positions": count,
            "mean_value_target": target_sums[side] / count if count else None,
        }

    return {
        "label": label,
        "source": str(source),
        "games": games,
        "positions": positions,
        "outcomes": dict(sorted(outcomes.items())),
        "terminations": dict(sorted(terminations.items())),
        "side_to_move": side_summary,
        "value_target_counts": dict(sorted(target_counts.items())),
        "errors": errors,
        "valid": not errors and games > 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, help="Baseline self_play_games.jsonl")
    parser.add_argument("--candidate", required=True, help="Candidate self_play_games.jsonl")
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--candidate-label", default="candidate")
    parser.add_argument("--output", required=True, help="Output JSON report path")
    args = parser.parse_args()

    report = {
        "schema_version": 1,
        "read_only": True,
        "baseline": audit_dataset(args.baseline, args.baseline_label),
        "candidate": audit_dataset(args.candidate, args.candidate_label),
    }
    report["valid"] = report["baseline"]["valid"] and report["candidate"]["valid"]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
