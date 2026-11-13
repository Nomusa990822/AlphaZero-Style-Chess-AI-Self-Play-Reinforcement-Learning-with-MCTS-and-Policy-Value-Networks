import numpy as np
import pytest

from src.training.tactical_benchmark import load_tactical_positions
from src.training.tactical_policy import (
    build_tactical_policy_examples,
    split_tactical_examples,
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
