import argparse
import hashlib
import json
from types import SimpleNamespace

import chess
import pytest

import benchmark_search_configs as benchmark
from benchmark_search_configs import estimate_simulations, parse_floats, parse_ints


def test_budget_counts_all_modes_and_configurations():
    assert estimate_simulations(13, [25, 50], [1.0, 1.5]) == 3900


@pytest.mark.parametrize("args", [(0, [25], [1.0]), (2, [], [1.0]), (2, [1], [])])
def test_budget_rejects_empty_dimensions(args):
    with pytest.raises(ValueError):
        estimate_simulations(*args)


@pytest.mark.parametrize("value", ["", "0", "-2", "1,1", "x"])
def test_integer_parser_rejects_invalid_values(value):
    with pytest.raises(Exception):
        parse_ints(value, "--simulations")


@pytest.mark.parametrize("value", ["", "0", "-1", "1.0,1.0", "x", "nan", "inf", "-inf"])
def test_float_parser_rejects_invalid_values(value):
    with pytest.raises(Exception):
        parse_floats(value, "--c-puct")


def test_parsers_accept_valid_values():
    assert parse_ints("25, 50", "--simulations") == [25, 50]
    assert parse_floats("1.0, 1.5", "--c-puct") == [1.0, 1.5]


def _args(checkpoint, **overrides):
    values = {
        "checkpoint": str(checkpoint),
        "positions": "fake-corpus.jsonl",
        "simulations": [2, 3],
        "c_puct": [1.0, 1.5],
        "max_positions": 10,
        "max_total_simulations": 100,
        "device": "cpu",
        "output": "unused.json",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_run_benchmark_executes_every_configuration_and_persists_valid_report(
    tmp_path, monkeypatch
):
    checkpoint = tmp_path / "model.pt"
    checkpoint.write_bytes(b"mock-checkpoint-bytes")
    cases = [
        SimpleNamespace(
            fen=chess.STARTING_FEN,
            position_id="start",
            acceptable_moves=["e2e4"],
        )
    ]
    search_configs = []
    model_constructions = []

    class FakeNetwork:
        def __init__(self, **kwargs):
            model_constructions.append(kwargs)

    class FakeInference:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeSearch:
        def __init__(self, inference, move_encoding, config):
            self.config = config
            search_configs.append(config)

        def run(self, board):
            return board

        def select_action(self, root, temperature):
            assert temperature == 0.0
            return chess.Move.from_uci("e2e4")

    score = SimpleNamespace(
        correct=1, accuracy=1.0, illegal=0,
        by_motif={"fork": 1.0}, by_color={"white": 1.0},
        by_phase={"opening": 1.0}, failures=(),
    )
    monkeypatch.setattr(benchmark, "load_tactical_positions", lambda path: cases)
    monkeypatch.setattr(benchmark, "resolve_device", lambda requested: "cpu")
    monkeypatch.setattr(
        benchmark, "MoveEncoding", lambda: SimpleNamespace(action_size=4672)
    )
    monkeypatch.setattr(benchmark, "AlphaZeroNet", FakeNetwork)
    monkeypatch.setattr(benchmark, "NetworkConfig", lambda **kwargs: kwargs)
    monkeypatch.setattr(
        benchmark, "load_checkpoint",
        lambda path, network, optimizer, map_location: {"epoch": 7},
    )
    monkeypatch.setattr(benchmark, "ModelInference", FakeInference)
    monkeypatch.setattr(
        benchmark, "MCTSConfig", lambda **kwargs: SimpleNamespace(**kwargs)
    )
    monkeypatch.setattr(benchmark, "MCTS", FakeSearch)
    monkeypatch.setattr(
        benchmark, "evaluate_tactical_selector", lambda positions, selector: score
    )

    report = benchmark.run_benchmark(_args(checkpoint))
    output = benchmark.write_report(report, tmp_path / "reports" / "sweep.json")
    persisted = json.loads(output.read_text(encoding="utf-8"))

    assert persisted == report
    assert len(search_configs) == 8
    assert len(model_constructions) == 1
    assert [c.use_tactical_root_filter for c in search_configs] == [True, False] * 4
    assert all(c.add_dirichlet_noise is False and c.temperature == 0.0 for c in search_configs)
    assert report["planned_total_simulations"] == 20
    assert report["checkpoint_sha256"] == hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    assert report["checkpoint_epoch"] == 7
    assert len(report["configurations"]) == 8
    assert all(item["correct"] == 1 and item["accuracy"] == 1.0 for item in report["configurations"])
    assert all(item["selections"][0]["selected_move"] == "e2e4" for item in report["configurations"])


def test_budget_is_rejected_before_model_construction(tmp_path, monkeypatch):
    checkpoint = tmp_path / "model.pt"
    checkpoint.write_bytes(b"checkpoint")
    monkeypatch.setattr(
        benchmark, "load_tactical_positions",
        lambda path: [SimpleNamespace(fen=chess.STARTING_FEN)],
    )
    monkeypatch.setattr(
        benchmark, "AlphaZeroNet",
        lambda **kwargs: pytest.fail("network must not be constructed for an over-budget run"),
    )
    with pytest.raises(ValueError, match="exceeds cap"):
        benchmark.run_benchmark(
            _args(checkpoint, simulations=[50], c_puct=[1.0], max_total_simulations=1)
        )


def test_missing_checkpoint_fails_before_loading_positions(monkeypatch, tmp_path):
    monkeypatch.setattr(
        benchmark, "load_tactical_positions",
        lambda path: pytest.fail("positions must not be loaded without a checkpoint"),
    )
    with pytest.raises(FileNotFoundError, match="Checkpoint not found"):
        benchmark.run_benchmark(_args(tmp_path / "missing.pt"))


def test_float_parser_accepts_small_finite_positive_values():
    assert parse_floats("0.000000000001", "--c-puct") == [0.000000000001]
