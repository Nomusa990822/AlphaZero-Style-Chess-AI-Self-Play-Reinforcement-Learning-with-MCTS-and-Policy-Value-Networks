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


@dataclass(frozen=True)
class TacticalSequencePly:
    """Accepted moves and explanation for one ply of a curated combination."""

    acceptable_moves: frozenset[str]
    annotation: str


@dataclass(frozen=True)
class TacticalSequence:
    """A reproducible principal variation illustrating a multi-motif combination."""

    sequence_id: str
    motifs: tuple[str, ...]
    fen: str
    plies: tuple[TacticalSequencePly, ...]
    phase: str

    @classmethod
    def from_dict(cls, data: dict) -> "TacticalSequence":
        required = {"id", "motifs", "fen", "plies", "phase"}
        missing = required.difference(data)
        if missing:
            raise ValueError(f"Missing tactical-sequence fields: {sorted(missing)}")

        sequence_id = str(data["id"]).strip()
        motifs = tuple(str(motif).strip().lower() for motif in data["motifs"])
        fen = str(data["fen"]).strip()
        phase = str(data["phase"]).strip().lower()
        raw_plies = data["plies"]
        if not sequence_id or not motifs or any(not motif for motif in motifs):
            raise ValueError("Sequence id and motif labels must be non-empty.")
        if any(motif not in TACTICAL_MOTIFS for motif in motifs):
            unknown = sorted(set(motifs).difference(TACTICAL_MOTIFS))
            raise ValueError(f"Sequence {sequence_id!r} has unknown motifs: {unknown}")
        if phase not in TACTICAL_PHASES:
            raise ValueError(f"Sequence {sequence_id!r} has unknown phase {phase!r}.")
        if not isinstance(raw_plies, list) or len(raw_plies) < 2:
            raise ValueError("A tactical sequence must contain at least two plies.")

        try:
            board = chess.Board(fen)
        except ValueError as exc:
            raise ValueError(f"Invalid FEN for sequence {sequence_id!r}: {exc}") from exc
        if not board.is_valid() or board.is_game_over(claim_draw=True):
            raise ValueError(f"Sequence {sequence_id!r} must start from a valid, non-terminal position.")

        plies: list[TacticalSequencePly] = []
        for index, raw_ply in enumerate(raw_plies, start=1):
            if not isinstance(raw_ply, dict) or not {"acceptable_moves", "annotation"}.issubset(raw_ply):
                raise ValueError(f"Sequence {sequence_id!r}, ply {index} is missing required fields.")
            moves = frozenset(str(move).strip() for move in raw_ply["acceptable_moves"])
            annotation = str(raw_ply["annotation"]).strip()
            if not moves or any(not move for move in moves) or not annotation:
                raise ValueError(f"Sequence {sequence_id!r}, ply {index} needs moves and an annotation.")
            legal_uci = {move.uci() for move in board.legal_moves}
            illegal = moves.difference(legal_uci)
            if illegal:
                raise ValueError(
                    f"Sequence {sequence_id!r}, ply {index} has illegal moves: {sorted(illegal)}"
                )
            plies.append(TacticalSequencePly(moves, annotation))
            # A representative accepted move advances validation to the next
            # position. The evaluator later checks the actual selected move.
            board.push(chess.Move.from_uci(sorted(moves)[0]))
            if index < len(raw_plies) and board.is_game_over(claim_draw=True):
                raise ValueError(f"Sequence {sequence_id!r} terminates before ply {index + 1}.")
        return cls(sequence_id, motifs, fen, tuple(plies), phase)


@dataclass(frozen=True)
class TacticalSequenceBenchmarkResult:
    total_sequences: int
    completed_sequences: int
    attempted_plies: int
    correct_plies: int
    illegal_moves: int
    sequence_completion_rate: float
    ply_accuracy: float
    by_combination: dict[str, dict[str, int | float]]
    by_color: dict[str, dict[str, int | float]]
    by_phase: dict[str, dict[str, int | float]]
    failures: tuple[dict, ...]


def load_tactical_sequences(path: str | Path) -> list[TacticalSequence]:
    """Load and validate tactical-combination JSONL records."""
    sequences: list[TacticalSequence] = []
    seen_ids: set[str] = set()
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                sequence = TacticalSequence.from_dict(json.loads(line))
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
            if sequence.sequence_id in seen_ids:
                raise ValueError(f"{path}:{line_number}: duplicate sequence id {sequence.sequence_id!r}")
            seen_ids.add(sequence.sequence_id)
            sequences.append(sequence)
    if not sequences:
        raise ValueError(f"No tactical sequences found in {path}.")
    return sequences


def evaluate_tactical_sequences(
    sequences: Iterable[TacticalSequence],
    select_move: Callable[[chess.Board], chess.Move | str],
) -> TacticalSequenceBenchmarkResult:
    """Measure complete-line success and per-ply accuracy on curated combinations.

    This replays a supplied principal variation and asks the selector to choose
    an accepted move at every ply. It measures line-following on the annotated
    line; it does not prove that the line is forced against every defence.
    """
    cases = list(sequences)
    if not cases:
        raise ValueError("At least one tactical sequence is required.")

    completed = attempted = correct = illegal = 0
    combination_groups: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total_sequences": 0, "completed_sequences": 0, "attempted_plies": 0, "correct_plies": 0}
    )
    color_groups: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "correct": 0, "illegal": 0}
    )
    phase_groups: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "correct": 0, "illegal": 0}
    )
    failures: list[dict] = []

    for case in cases:
        board = chess.Board(case.fen)
        combination = "+".join(case.motifs)
        combo = combination_groups[combination]
        combo["total_sequences"] += 1
        sequence_ok = True
        for ply_index, ply in enumerate(case.plies, start=1):
            color = "white" if board.turn == chess.WHITE else "black"
            color_group = color_groups[color]
            phase_group = phase_groups[case.phase]
            attempted += 1
            combo["attempted_plies"] += 1
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
                color_group["illegal"] += 1
                phase_group["illegal"] += 1
                failures.append({
                    "id": case.sequence_id,
                    "ply": ply_index,
                    "side_to_move": color,
                    "selected": "ILLEGAL",
                    "acceptable_moves": sorted(ply.acceptable_moves),
                })
                sequence_ok = False
                break

            if selected_uci not in ply.acceptable_moves:
                failures.append({
                    "id": case.sequence_id,
                    "ply": ply_index,
                    "side_to_move": color,
                    "selected": selected_uci,
                    "acceptable_moves": sorted(ply.acceptable_moves),
                })
                sequence_ok = False
                break

            correct += 1
            combo["correct_plies"] += 1
            color_group["correct"] += 1
            phase_group["correct"] += 1
            board.push(move)

        if sequence_ok:
            completed += 1
            combo["completed_sequences"] += 1

    def rates(groups: dict[str, dict[str, int]]) -> dict[str, dict[str, int | float]]:
        rendered = {}
        for key, counts in sorted(groups.items()):
            total = counts["total"]
            rendered[key] = {
                **counts,
                "accuracy": counts["correct"] / total if total else 0.0,
            }
        return rendered

    by_combination = {}
    for key, counts in sorted(combination_groups.items()):
        by_combination[key] = {
            **counts,
            "completion_rate": counts["completed_sequences"] / counts["total_sequences"],
            "ply_accuracy": counts["correct_plies"] / counts["attempted_plies"] if counts["attempted_plies"] else 0.0,
        }

    return TacticalSequenceBenchmarkResult(
        total_sequences=len(cases),
        completed_sequences=completed,
        attempted_plies=attempted,
        correct_plies=correct,
        illegal_moves=illegal,
        sequence_completion_rate=completed / len(cases),
        ply_accuracy=correct / attempted if attempted else 0.0,
        by_combination=by_combination,
        by_color=rates(color_groups),
        by_phase=rates(phase_groups),
        failures=tuple(failures),
    )
