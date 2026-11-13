import json
import sys
from types import SimpleNamespace

import chess
import torch

import compare_tactical_filters


def test_main_runs_paired_modes_on_same_checkpoint_and_writes_report(
    monkeypatch, tmp_path, capsys
):
    checkpoint = tmp_path / "checkpoint.pt"
    checkpoint.write_bytes(b"fake checkpoint")
    output = tmp_path / "reports" / "paired.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "compare_tactical_filters.py",
            "--checkpoint", str(checkpoint),
            "--simulations", "9",
            "--device", "cpu",
            "--output", str(output),
        ],
    )

    position = SimpleNamespace(
        position_id="opening-e4",
        motif="fork",
        fen=chess.STARTING_FEN,
        acceptable_moves=frozenset({"e2e4"}),
        phase="opening",
    )
    monkeypatch.setattr(
        compare_tactical_filters, "load_tactical_positions", lambda path: [position]
    )
    monkeypatch.setattr(
        compare_tactical_filters, "resolve_device", lambda requested: torch.device("cpu")
    )

    class FakeEncoding:
        action_size = 4672

    class FakeSearch:
        def __init__(self, inference, move_encoding, config):
            self.enabled = config.use_tactical_root_filter
            assert config.num_simulations == 9
            assert config.add_dirichlet_noise is False
            assert config.temperature == 0.0

        def run(self, board):
            assert board.fen() == chess.STARTING_FEN
            return "root"

        def select_action(self, root, temperature):
            assert root == "root"
            return chess.Move.from_uci("e2e4" if self.enabled else "d2d4")

    monkeypatch.setattr(compare_tactical_filters, "MoveEncoding", FakeEncoding)
    monkeypatch.setattr(compare_tactical_filters, "BoardEncoder", lambda: "encoder")
    monkeypatch.setattr(compare_tactical_filters, "AlphaZeroNet", lambda **kwargs: "network")
    monkeypatch.setattr(
        compare_tactical_filters,
        "NetworkConfig",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )
    monkeypatch.setattr(
        compare_tactical_filters, "load_checkpoint", lambda *args, **kwargs: {"epoch": 12}
    )
    monkeypatch.setattr(
        compare_tactical_filters,
        "ModelInference",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )
    monkeypatch.setattr(compare_tactical_filters, "MCTS", FakeSearch)

    compare_tactical_filters.main()

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["checkpoint_epoch"] == 12
    assert report["simulations_per_position"] == 9
    assert report["paired"] is True
    assert report["summary"]["filter_on"]["correct"] == 1
    assert report["summary"]["filter_off"]["correct"] == 0
    assert report["comparison"]["accuracy_delta_filter_on_minus_off"] == 1.0
    assert report["comparison"]["positions_with_changed_selection"] == 1
    assert report["positions"][0]["filter_on"]["selected_move"] == "e2e4"
    assert report["positions"][0]["filter_off"]["selected_move"] == "d2d4"
    assert "Saved paired benchmark report:" in capsys.readouterr().out
