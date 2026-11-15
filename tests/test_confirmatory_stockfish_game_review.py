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


def test_san_tokenizer_handles_move_numbers_and_results():
    assert MODULE.san_tokens('[Result "1-0"]\n\n1. e4 e5 2. Nf3 Nc6 1-0') == [
        "e4", "e5", "Nf3", "Nc6"
    ]
