import json

import chess
import chess.pgn

from scripts.audit_self_play_datasets import audit_dataset


def _record(result="1-0"):
    board = chess.Board()
    moves = ["e2e4", "e7e5", "g1f3"]
    targets = []
    for ply, move_uci in enumerate(moves):
        white_value = 1.0 if result == "1-0" else -1.0 if result == "0-1" else 0.0
        targets.append({
            "ply": ply,
            "fen": board.fen(),
            "side_to_move": "white" if board.turn == chess.WHITE else "black",
            "value_target": white_value if board.turn == chess.WHITE else -white_value,
        })
        board.push_uci(move_uci)

    game = chess.pgn.Game()
    game.headers["Result"] = result
    node = game
    board = game.board()
    for move_uci in moves:
        move = chess.Move.from_uci(move_uci)
        node = node.add_variation(move)
        board.push(move)
    import io
    stream = io.StringIO()
    print(game, file=stream)
    return {
        "result": result,
        "pgn": stream.getvalue().strip(),
        "move_count": len(moves),
        "termination": "test",
        "position_targets": targets,
    }


def test_audit_counts_games_positions_and_side_to_move(tmp_path):
    path = tmp_path / "games.jsonl"
    path.write_text(json.dumps(_record()) + "\n", encoding="utf-8")

    result = audit_dataset(path, "baseline")

    assert result["valid"] is True
    assert result["games"] == 1
    assert result["positions"] == 3
    assert result["outcomes"] == {"1-0": 1}
    assert result["side_to_move"]["white"]["positions"] == 2
    assert result["side_to_move"]["black"]["positions"] == 1
    assert result["errors"] == []


def test_audit_rejects_a_corrupted_value_target(tmp_path):
    record = _record()
    record["position_targets"][1]["value_target"] = 1.0
    path = tmp_path / "games.jsonl"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    result = audit_dataset(path, "candidate")

    assert result["valid"] is False
    assert result["games"] == 0
    assert "value target mismatch" in result["errors"][0]


def test_audit_rejects_legacy_pgn_only_records(tmp_path):
    path = tmp_path / "legacy.jsonl"
    path.write_text(json.dumps({"result": "1/2-1/2", "pgn": "", "move_count": 0}) + "\n", encoding="utf-8")

    result = audit_dataset(path, "legacy")

    assert result["valid"] is False
    assert "missing position_targets" in result["errors"][0]
