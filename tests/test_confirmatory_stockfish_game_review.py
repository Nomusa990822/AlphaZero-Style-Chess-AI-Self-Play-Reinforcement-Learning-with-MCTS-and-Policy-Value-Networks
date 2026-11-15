from __future__ import annotations

import importlib.util
from pathlib import Path

import chess
import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "analyse_confirmatory_games_stockfish.py"
SPEC = importlib.util.spec_from_file_location("confirmatory_stockfish_review", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def record_for(moves: list[str], *, result: str = "1-0") -> dict:
    board = chess.Board()
    san = []
    for uci in moves:
        move = chess.Move.from_uci(uci)
        san.append(f"{board.fullmove_number}{'.' if board.turn else '...'} {board.san(move)}")
        board.push(move)
    movetext = " ".join(san) + " " + result
    return {
        "opening_id": "fixture",
        "starting_fen": chess.STARTING_FEN,
        "uci_moves": moves,
        "plies": len(moves),
        "result": result,
        "pgn": '[Result "' + result + '"]\n\n' + movetext,
    }


def test_replay_record_validates_san_and_uci():
    item = record_for(["e2e4", "e7e5", "g1f3"])
    positions, final_board = MODULE.replay_record(item)
    assert len(positions) == 3
    assert final_board.fullmove_number == 2
    assert positions[0][2] == "e4"


def test_replay_record_rejects_illegal_uci():
    item = record_for(["e2e4"])
    item["uci_moves"] = ["e2e5"]
    with pytest.raises(ValueError, match="illegal UCI"):
        MODULE.replay_record(item)


def test_replay_record_rejects_san_uci_mismatch():
    item = record_for(["e2e4"])
    item["pgn"] = '[Result "1-0"]\n\n1. d4 1-0'
    with pytest.raises(ValueError, match="SAN"):
        MODULE.replay_record(item)


def test_select_records_uses_four_losses_four_draws_and_white_win():
    records = []
    for opening_id in MODULE.LOSS_IDS:
        records.append({"opening_id": opening_id, "leg": "candidate_white", "candidate_outcome": "loss"})
    for opening_id in MODULE.DRAW_IDS:
        records.append({"opening_id": opening_id, "leg": "candidate_white", "candidate_outcome": "draw"})
    for opening_id in MODULE.WIN_IDS:
        records.append({"opening_id": opening_id, "leg": "candidate_white", "candidate_outcome": "win"})
    selected = MODULE.select_records({"game_records": records})
    assert len(selected) == 9
    assert {item["candidate_outcome"] for item in selected} == {"loss", "draw", "win"}


def test_select_records_rejects_wrong_outcome():
    records = [
        {"opening_id": opening_id, "leg": "candidate_white", "candidate_outcome": "draw"}
        for opening_id in MODULE.LOSS_IDS | MODULE.DRAW_IDS | MODULE.WIN_IDS
    ]
    with pytest.raises(ValueError, match="not a recorded candidate-White loss"):
        MODULE.select_records({"game_records": records})


def test_replay_record_handles_pgn_opening_preamble_before_recorded_fen():
    opening = chess.Board()
    prelude = ["e2e4", "e7e5", "g1f3", "b8c6"]
    san_prefix = []
    for uci in prelude:
        move = chess.Move.from_uci(uci)
        san_prefix.append(f"{opening.fullmove_number}{'.' if opening.turn else '...'} {opening.san(move)}")
        opening.push(move)

    continuation = ["f1c4", "g8f6", "d2d3"]
    record = record_for(continuation)
    record["starting_fen"] = opening.fen()
    continuation_board = opening.copy()
    san_continuation = []
    for uci in continuation:
        move = chess.Move.from_uci(uci)
        san_continuation.append(f"{continuation_board.fullmove_number}{'.' if continuation_board.turn else '...'} {continuation_board.san(move)}")
        continuation_board.push(move)
    record["pgn"] = (
        '[Result "1-0"]\n\n'
        + " ".join(san_prefix + san_continuation)
        + " 1-0"
    )

    positions, final_board = MODULE.replay_record(record)
    assert len(positions) == len(continuation)
    assert positions[0][0].fen() == opening.fen()
    assert final_board.fen() == continuation_board.fen()
