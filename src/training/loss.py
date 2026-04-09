"""
AlphaZero-style loss:
- policy loss: cross-entropy against MCTS target distribution
- value loss: mean squared error
- total loss = policy + value
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F


@dataclass
class LossBreakdown:
    """
    Stores detached scalar loss values for logging.
    """
    total_loss: float
    policy_loss: float
    value_loss: float


def alphazero_loss(
    policy_logits: torch.Tensor,
    value_pred: torch.Tensor,
    policy_target: torch.Tensor,
    value_target: torch.Tensor,
) -> tuple[torch.Tensor, LossBreakdown]:
    """
    Compute AlphaZero loss.

    Args:
        policy_logits: (B, action_size)
        value_pred: (B, 1)
        policy_target: (B, action_size)
        value_target: (B, 1)

    Returns:
        total_loss tensor
        LossBreakdown for logging
    """
    log_probs = F.log_softmax(policy_logits, dim=1)
    policy_loss = -(policy_target * log_probs).sum(dim=1).mean()

    value_loss = F.mse_loss(value_pred, value_target)

    total_loss = policy_loss + value_loss

    breakdown = LossBreakdown(
        total_loss=float(total_loss.detach().item()),
        policy_loss=float(policy_loss.detach().item()),
        value_loss=float(value_loss.detach().item()),
    )
    return total_loss, breakdown
