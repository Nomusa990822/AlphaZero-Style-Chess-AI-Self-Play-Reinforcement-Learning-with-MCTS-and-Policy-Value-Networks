import json
import sys
from types import SimpleNamespace

import chess
import pytest
import torch

import evaluate_tactics


def test_resolve_device_accepts_cpu():
    assert evaluate_tactics.resolve_device("cpu") == torch.device("cpu")


def test_resolve_device_rejects_unavailable_cuda(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)

    with pytest.raises(RuntimeError, match="CUDA was requested"):
        evaluate_tactics.resolve_device("cuda")


def test_main_runs_deterministic_search_and_writes_json_report(
    monkeypatch, tmp_path, capsys
):
    checkpoint = tmp_path / "checkpoint.pt"
    checkpoint.write_bytes(b"test checkpoint")
    output = tmp_path / "reports" / "tactics.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "evaluate_tactics.py",
            "--checkpoint",
            str(checkpoint),
            "--simulations",
            "17",
            "--device",
            "cpu",
            "--output",
            str(output),
        ],
    )

    positions = [object()]
    monkeypatch.setattr(evaluate_tactics, "load_tactical_positions", lambda path: positions)
    monkeypatch.setattr(evaluate_tactics, "resolve_device", lambda requested: torch.device("cpu"))

    class FakeEncoding:
        action_size = 4672

    class FakeSearch:
        def __init__(self, inference, move_encoding, config):
            self.config = config

        def run(self, board):
            assert isinstance(board, chess.Board)
            return "root"

        def select_action(self, root, temperature):
            assert root == "root"
            assert temperature == 0.0
            return "e2e4"

    captured = {}
    monkeypatch.setattr(evaluate_tactics, "MoveEncoding", FakeEncoding)
    monkeypatch.setattr(evaluate_tactics, "BoardEncoder", lambda: "encoder")
    monkeypatch.setattr(evaluate_tactics, "AlphaZeroNet", lambda **kwargs: "network")
    monkeypatch.setattr(
        evaluate_tactics,
        "NetworkConfig",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )
    monkeypatch.setattr(
        evaluate_tactics,
        "load_checkpoint",
        lambda *args, **kwargs: {"epoch": 7},
    )
    monkeypatch.setattr(
        evaluate_tactics,
        "ModelInference",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )

    def fake_config(**kwargs):
        captured["config"] = kwargs
        return SimpleNamespace(**kwargs)

    monkeypatch.setattr(evaluate_tactics, "MCTSConfig", fake_config)
    monkeypatch.setattr(evaluate_tactics, "MCTS", FakeSearch)

    def fake_evaluate(cases, selector):
        assert cases is positions
        assert selector(chess.Board()) == "e2e4"
        return SimpleNamespace(
            total=1,
            correct=1,
            illegal=0,
            accuracy=1.0,
            by_motif={"fork": {"total": 1, "correct": 1, "accuracy": 1.0}},
            by_color={"white": {"total": 1, "correct": 1, "illegal": 0, "accuracy": 1.0}},
            by_phase={"middlegame": {"total": 1, "correct": 1, "illegal": 0, "accuracy": 1.0}},
            failures=(),
        )

    monkeypatch.setattr(
        evaluate_tactics,
        "evaluate_tactical_selector",
        fake_evaluate,
    )

    evaluate_tactics.main()

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["checkpoint"] == str(checkpoint)
    assert report["checkpoint_epoch"] == 7
    assert report["device"] == "cpu"
    assert report["simulations"] == 17
    assert report["tactical_root_filter"] is True
    assert report["accuracy"] == 1.0
    assert report["by_color"]["white"]["accuracy"] == 1.0
    assert report["by_phase"]["middlegame"]["accuracy"] == 1.0
    assert report["failures"] == []
    assert captured["config"] == {
        "num_simulations": 17,
        "add_dirichlet_noise": False,
        "temperature": 0.0,
        "use_tactical_root_filter": True,
    }
    assert "Saved benchmark report:" in capsys.readouterr().out


def test_main_rejects_missing_checkpoint(monkeypatch, tmp_path):
    missing = tmp_path / "missing.pt"
    monkeypatch.setattr(
        sys,
        "argv",
        ["evaluate_tactics.py", "--checkpoint", str(missing)],
    )

    with pytest.raises(FileNotFoundError, match="Checkpoint not found"):
        evaluate_tactics.main()
