import numpy as np
import pytest
import torch

from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.tactical_benchmark import load_tactical_positions
from src.training.tactical_policy import (
    build_tactical_policy_examples,
    configure_policy_head_only,
    set_policy_head_training_mode,
    split_tactical_examples,
    value_drift_metrics,
    value_predictions,
)


def small_model():
    return AlphaZeroNet(
        action_size=4672,
        config=NetworkConfig(
            input_channels=20, board_size=8, num_filters=8,
            num_res_blocks=1, value_hidden_size=16,
        ),
    )


def test_tactical_targets_are_uniform_over_acceptable_legal_moves():
    positions = load_tactical_positions("benchmarks/tactical_positions.jsonl")
    examples = build_tactical_policy_examples(positions[:3])
    assert examples[0].state.shape == (20, 8, 8)
    assert examples[0].policy_target.shape == (4672,)
    nonzero = examples[0].policy_target[examples[0].policy_target > 0]
    assert len(nonzero) == 1
    assert np.isclose(float(nonzero.sum()), 1.0)


def test_black_to_move_is_preserved_in_example():
    positions = load_tactical_positions("benchmarks/tactical_positions.jsonl")
    black_case = next(
        case for case in positions
        if __import__("chess").Board(case.fen).turn == __import__("chess").BLACK
    )
    example = build_tactical_policy_examples([black_case])[0]
    assert example.side_to_move is False
    assert np.isclose(float(example.policy_target.sum()), 1.0)


def test_split_is_deterministic_disjoint_and_complete():
    positions = load_tactical_positions("benchmarks/tactical_positions.jsonl")
    examples = build_tactical_policy_examples(positions)
    train_a, validation_a = split_tactical_examples(examples, seed=42)
    train_b, validation_b = split_tactical_examples(examples, seed=42)
    assert [x.position_id for x in train_a] == [x.position_id for x in train_b]
    assert [x.position_id for x in validation_a] == [x.position_id for x in validation_b]
    assert not ({x.position_id for x in train_a} & {x.position_id for x in validation_a})
    assert len(train_a) + len(validation_a) == len(examples)


def test_split_rejects_too_few_examples():
    with pytest.raises(ValueError, match="five examples"):
        split_tactical_examples([], seed=1)


def test_policy_head_only_training_preserves_value_predictions_and_shared_trunk():
    torch.manual_seed(7)
    positions = load_tactical_positions("benchmarks/tactical_positions.jsonl")[:8]
    examples = build_tactical_policy_examples(positions)
    model = small_model()
    before = value_predictions(model, examples)
    trunk_before = [p.detach().clone() for p in model.input_block.parameters()]
    value_before = [p.detach().clone() for p in model.value_head.parameters()]

    trainable = configure_policy_head_only(model)
    assert trainable
    assert all(p.requires_grad for p in model.policy_head.parameters())
    assert not any(p.requires_grad for p in model.input_block.parameters())
    assert not any(p.requires_grad for p in model.res_blocks.parameters())
    assert not any(p.requires_grad for p in model.value_head.parameters())

    optimizer = torch.optim.Adam(trainable, lr=1e-3)
    set_policy_head_training_mode(model)
    states = torch.as_tensor(np.stack([x.state for x in examples]), dtype=torch.float32)
    targets = torch.as_tensor(np.stack([x.policy_target for x in examples]), dtype=torch.float32)
    logits, _ = model(states)
    loss = -(targets * torch.log_softmax(logits, dim=1)).sum(dim=1).mean()
    loss.backward()
    optimizer.step()

    after = value_predictions(model, examples)
    assert np.array_equal(before, after)
    assert all(torch.equal(old, new) for old, new in zip(trunk_before, model.input_block.parameters()))
    assert all(torch.equal(old, new) for old, new in zip(value_before, model.value_head.parameters()))
    assert any(p.grad is not None for p in model.policy_head.parameters())


def test_value_drift_metrics_reports_per_position_changes():
    result = value_drift_metrics(np.array([0.1, -0.2]), np.array([0.2, -0.1]))
    assert result["positions"] == 2
    assert result["mean_absolute_change"] == pytest.approx(0.1)
    assert result["maximum_absolute_change"] == pytest.approx(0.1)
    assert result["root_mean_square_change"] == pytest.approx(0.1)


def test_value_drift_metrics_rejects_unaligned_predictions():
    with pytest.raises(ValueError, match="aligned"):
        value_drift_metrics(np.array([0.1]), np.array([0.1, 0.2]))
