import json

import chess
import pytest

from src.training.tactical_benchmark import (
    TacticalPosition,
    evaluate_tactical_selector,
    load_tactical_positions,
)


def position(position_id="fork-1", motif="fork", fen=None, moves=None):
    return TacticalPosition.from_dict({
        "id": position_id,
        "motif": motif,
        "fen": fen or chess.STARTING_FEN,
        "acceptable_moves": moves or ["e2e4"],
    })


def test_tactical_position_validates_acceptable_moves():
    case = position()
    assert case.position_id == "fork-1"
    assert case.acceptable_moves == frozenset({"e2e4"})


def test_tactical_position_rejects_illegal_acceptable_move():
    with pytest.raises(ValueError, match="illegal acceptable moves"):
        position(moves=["e2e5"])


def test_tactical_position_rejects_unknown_motif():
    with pytest.raises(ValueError, match="unknown motif"):
        position(motif="forkish")


def test_tactical_position_rejects_structurally_invalid_fen():
    # The kings are adjacent, which cannot occur in a legal chess position.
    invalid_fen = "8/8/8/8/8/8/4k3/4K3 w - - 0 1"

    with pytest.raises(ValueError, match="invalid chess position"):
        position(fen=invalid_fen)


def test_benchmark_reports_overall_and_per_motif_accuracy():
    cases = [
        position("fork-1", "fork", moves=["e2e4"]),
        position("pin-1", "pin", moves=["d2d4"]),
        position("fork-2", "fork", moves=["g1f3"]),
    ]
    chosen = iter(["e2e4", "e2e4", "g1f3"])

    result = evaluate_tactical_selector(cases, lambda board: next(chosen))

    assert result.total == 3
    assert result.correct == 2
    assert result.illegal == 0
    assert result.accuracy == pytest.approx(2 / 3)
    assert result.by_motif["fork"]["total"] == 2
    assert result.by_motif["fork"]["accuracy"] == 1.0
    assert result.by_motif["pin"]["accuracy"] == 0.0
    assert result.failures == (
        {"id": "pin-1", "motif": "pin", "selected": "e2e4"},
    )


def test_benchmark_counts_illegal_selector_outputs():
    result = evaluate_tactical_selector(
        [position()],
        lambda board: "e2e5",
    )

    assert result.correct == 0
    assert result.illegal == 1
    assert result.accuracy == 0.0
    assert result.failures[0]["selected"] == "ILLEGAL"


def test_benchmark_loader_validates_jsonl_and_duplicate_ids(tmp_path):
    path = tmp_path / "positions.jsonl"
    record = {
        "id": "case-1",
        "motif": "fork",
        "fen": chess.STARTING_FEN,
        "acceptable_moves": ["e2e4"],
    }
    path.write_text(
        json.dumps(record) + "\n" + json.dumps(record) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate id"):
        load_tactical_positions(path)


def test_benchmark_loader_rejects_empty_corpus(tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_text("# Add curated positions as JSONL records.\n", encoding="utf-8")

    with pytest.raises(ValueError, match="No tactical positions"):
        load_tactical_positions(path)
