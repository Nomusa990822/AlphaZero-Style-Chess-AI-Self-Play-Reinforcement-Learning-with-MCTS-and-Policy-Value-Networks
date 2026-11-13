"""Policy-only supervision utilities for curated tactical positions.

Tactical labels supervise move selection only. They deliberately do not create
value targets: value learning remains grounded in completed self-play games.
"""
from __future__ import annotations

from dataclasses import dataclass
import random

import chess
import numpy as np

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.training.tactical_benchmark import TacticalPosition


@dataclass(frozen=True)
class TacticalPolicyExample:
    position_id: str
    motif: str
    state: np.ndarray
    policy_target: np.ndarray
    side_to_move: bool


def build_tactical_policy_examples(
    positions: list[TacticalPosition],
    encoder: BoardEncoder | None = None,
    move_encoding: MoveEncoding | None = None,
) -> list[TacticalPolicyExample]:
    """Encode validated positions with uniform probability over accepted moves."""
    board_encoder = encoder or BoardEncoder()
    encoding = move_encoding or MoveEncoding()
    examples = []
    for case in positions:
        board = chess.Board(case.fen)
        target = np.zeros(encoding.action_size, dtype=np.float32)
        indices = sorted({
            encoding.move_to_tensor_index(chess.Move.from_uci(uci), board)
            for uci in case.acceptable_moves
        })
        if not indices:
            raise ValueError(f"{case.position_id}: no acceptable policy actions")
        target[indices] = 1.0 / len(indices)
        examples.append(TacticalPolicyExample(
            position_id=case.position_id,
            motif=case.motif,
            state=board_encoder.encode(board),
            policy_target=target,
            side_to_move=board.turn,
        ))
    if not examples:
        raise ValueError("At least one tactical position is required.")
    return examples


def split_tactical_examples(
    examples: list[TacticalPolicyExample],
    validation_fraction: float = 0.2,
    seed: int = 20261113,
) -> tuple[list[TacticalPolicyExample], list[TacticalPolicyExample]]:
    """Deterministic holdout split; validation examples never enter optimisation."""
    if len(examples) < 5:
        raise ValueError("At least five examples are required for a train/validation split.")
    if not 0.0 < validation_fraction < 0.5:
        raise ValueError("validation_fraction must be between 0 and 0.5.")
    indices = list(range(len(examples)))
    random.Random(seed).shuffle(indices)
    validation_count = max(1, round(len(examples) * validation_fraction))
    validation_indices = set(indices[:validation_count])
    train = [item for i, item in enumerate(examples) if i not in validation_indices]
    validation = [item for i, item in enumerate(examples) if i in validation_indices]
    return train, validation


def configure_policy_head_only(model) -> list:
    """Freeze the shared trunk and value head; return policy-head parameters.

    Freezing the trunk is essential: freezing only the value head still changes
    value predictions when shared representations are updated.
    """
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    for parameter in model.policy_head.parameters():
        parameter.requires_grad_(True)
    return list(model.policy_head.parameters())


def set_policy_head_training_mode(model) -> None:
    """Train policy-head BatchNorm while keeping trunk/value BatchNorm in eval."""
    model.eval()
    model.policy_head.train()


def value_predictions(model, examples, device: str = "cpu") -> np.ndarray:
    """Return per-position side-to-move values in stable example order."""
    import torch

    if not examples:
        raise ValueError("At least one evaluation example is required.")
    states = torch.as_tensor(
        np.stack([x.state for x in examples]), dtype=torch.float32, device=device
    )
    model.eval()
    with torch.no_grad():
        _, values = model(states)
    return values.detach().cpu().numpy().reshape(-1).astype(np.float64)


def value_drift_metrics(before: np.ndarray, after: np.ndarray) -> dict:
    """Quantify per-position value changes between two checkpoint states."""
    before = np.asarray(before, dtype=np.float64).reshape(-1)
    after = np.asarray(after, dtype=np.float64).reshape(-1)
    if before.shape != after.shape or before.size == 0:
        raise ValueError("Before/after value predictions must be non-empty and aligned.")
    delta = after - before
    absolute = np.abs(delta)
    return {
        "positions": int(before.size),
        "mean_absolute_change": float(absolute.mean()),
        "maximum_absolute_change": float(absolute.max()),
        "root_mean_square_change": float(np.sqrt(np.mean(np.square(delta)))),
        "mean_before": float(before.mean()),
        "mean_after": float(after.mean()),
    }


def policy_metrics(model, examples, device: str = "cpu") -> dict:
    """Report top-1 accuracy and accepted-policy probability mass."""
    import torch

    if not examples:
        raise ValueError("At least one evaluation example is required.")
    states = torch.as_tensor(np.stack([x.state for x in examples]), dtype=torch.float32, device=device)
    targets = torch.as_tensor(np.stack([x.policy_target for x in examples]), dtype=torch.float32, device=device)
    model.eval()
    with torch.no_grad():
        logits, values = model(states)
        log_probs = torch.log_softmax(logits, dim=1)
        losses = -(targets * log_probs).sum(dim=1)
        predicted = logits.argmax(dim=1)
        accepted = targets > 0
        top1 = accepted.gather(1, predicted.unsqueeze(1)).squeeze(1)
        accepted_mass = (torch.softmax(logits, dim=1) * accepted).sum(dim=1)
    return {
        "positions": len(examples),
        "policy_cross_entropy": float(losses.mean().item()),
        "top1_acceptable": int(top1.sum().item()),
        "top1_accuracy": float(top1.float().mean().item()),
        "mean_acceptable_probability_mass": float(accepted_mass.mean().item()),
        "mean_value_prediction_side_to_move": float(values.mean().item()),
    }
