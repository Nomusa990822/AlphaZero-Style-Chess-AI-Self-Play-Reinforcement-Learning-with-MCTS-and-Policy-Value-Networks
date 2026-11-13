"""Reusable tactical-position benchmark utilities.

The benchmark scores a move selector against curated acceptable-move sets.
It deliberately does not infer chess motifs or label moves as tactically sound:
the position corpus supplies those human-validated labels.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable, Iterable

import chess


TACTICAL_PHASES = frozenset({"opening", "middlegame", "endgame"})


TACTICAL_MOTIFS = frozenset({
    "mating_net",
    "fork",
    "hanging_piece",
    "pin",
    "skewer",
    "discovered_attack",
    "double_attack",
    "deflection",
    "decoy",
    "overloaded_defender",
    "trapped_piece",
    "defensive_resource",
    "endgame_tactic",
})


@dataclass(frozen=True)
class TacticalPosition:
    """One benchmark position and its curated acceptable first moves."""

    position_id: str
    motif: str
    fen: str
    acceptable_moves: frozenset[str]
    annotation: str
    phase: str

    @classmethod
    def from_dict(cls, data: dict) -> "TacticalPosition":
        required = {"id", "motif", "fen", "acceptable_moves", "annotation", "phase"}
        missing = required.difference(data)
        if missing:
            raise ValueError(f"Missing tactical-position fields: {sorted(missing)}")

        position_id = str(data["id"]).strip()
        motif = str(data["motif"]).strip().lower()
        fen = str(data["fen"]).strip()
        moves = frozenset(str(move).strip() for move in data["acceptable_moves"])
        annotation = str(data["annotation"]).strip()
        phase = str(data["phase"]).strip().lower()
        if not position_id or not motif or not moves or any(not move for move in moves):
            raise ValueError("Position id, motif, and acceptable moves must be non-empty.")
        if not annotation:
            raise ValueError(f"Position {position_id!r} must include a non-empty tactical annotation.")
        if phase not in TACTICAL_PHASES:
            raise ValueError(
                f"Position {position_id!r} has unknown phase {phase!r}; "
                f"expected one of {sorted(TACTICAL_PHASES)}."
            )
        if motif not in TACTICAL_MOTIFS:
            raise ValueError(
                f"Position {position_id!r} has unknown motif {motif!r}; "
                f"expected one of {sorted(TACTICAL_MOTIFS)}."
            )

        try:
            board = chess.Board(fen)
        except ValueError as exc:
            raise ValueError(f"Invalid FEN for position {position_id!r}: {exc}") from exc
        if not board.is_valid():
            raise ValueError(
                f"Position {position_id!r} is an invalid chess position "
                f"(python-chess status: {board.status()})."
            )
        if board.is_game_over(claim_draw=True):
            raise ValueError(f"Position {position_id!r} is already terminal.")

        legal_uci = {move.uci() for move in board.legal_moves}
        illegal = moves.difference(legal_uci)
        if illegal:
            raise ValueError(
                f"Position {position_id!r} has illegal acceptable moves: {sorted(illegal)}"
            )
        return cls(position_id, motif, fen, moves, annotation, phase)


@dataclass(frozen=True)
class TacticalBenchmarkResult:
    total: int
    correct: int
    illegal: int
    accuracy: float
    by_motif: dict[str, dict[str, int | float]]
    by_color: dict[str, dict[str, int | float]]
    by_phase: dict[str, dict[str, int | float]]
    failures: tuple[dict[str, str], ...]


def load_tactical_positions(path: str | Path) -> list[TacticalPosition]:
    """Load validated JSONL positions; blank lines and comments are ignored."""
    positions: list[TacticalPosition] = []
    seen_ids: set[str] = set()
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                position = TacticalPosition.from_dict(json.loads(line))
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
            if position.position_id in seen_ids:
                raise ValueError(f"{path}:{line_number}: duplicate id {position.position_id!r}")
            seen_ids.add(position.position_id)
            positions.append(position)
    if not positions:
        raise ValueError(f"No tactical positions found in {path}.")
    return positions


def evaluate_tactical_selector(
    positions: Iterable[TacticalPosition],
    select_move: Callable[[chess.Board], chess.Move | str],
) -> TacticalBenchmarkResult:
    """Score a deterministic move selector against accepted UCI move sets."""
    cases = list(positions)
    if not cases:
        raise ValueError("At least one tactical position is required.")

    correct = 0
    illegal = 0
    grouped: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "correct": 0, "illegal": 0}
    )
    failures: list[dict[str, str]] = []
    color_groups: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "correct": 0, "illegal": 0}
    )
    phase_groups: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "correct": 0, "illegal": 0}
    )

    for case in cases:
        board = chess.Board(case.fen)
        group = grouped[case.motif]
        color = "white" if board.turn == chess.WHITE else "black"
        color_group = color_groups[color]
        phase_group = phase_groups[case.phase]
        group["total"] += 1
        color_group["total"] += 1
        phase_group["total"] += 1
        try:
            selected = select_move(board.copy(stack=True))
            move = selected if isinstance(selected, chess.Move) else chess.Move.from_uci(str(selected))
            if move not in board.legal_moves:
                raise ValueError("selector returned an illegal move")
            selected_uci = move.uci()
        except (ValueError, TypeError):
            illegal += 1
            group["illegal"] += 1
            color_group["illegal"] += 1
            phase_group["illegal"] += 1
            failures.append({"id": case.position_id, "motif": case.motif, "selected": "ILLEGAL"})
            continue

        if selected_uci in case.acceptable_moves:
            correct += 1
            group["correct"] += 1
            color_group["correct"] += 1
            phase_group["correct"] += 1
        else:
            failures.append({
                "id": case.position_id,
                "motif": case.motif,
                "selected": selected_uci,
            })

    total = len(cases)
    by_motif = {
        motif: {
            **counts,
            "accuracy": counts["correct"] / counts["total"],
        }
        for motif, counts in sorted(grouped.items())
    }
    by_color = {
        color: {
            **counts,
            "accuracy": counts["correct"] / counts["total"],
        }
        for color, counts in sorted(color_groups.items())
    }
    by_phase = {
        phase: {
            **counts,
            "accuracy": counts["correct"] / counts["total"],
        }
        for phase, counts in sorted(phase_groups.items())
    }
    return TacticalBenchmarkResult(
        total=total,
        correct=correct,
        illegal=illegal,
        accuracy=correct / total,
        by_motif=by_motif,
        by_color=by_color,
        by_phase=by_phase,
        failures=tuple(failures),
    )
