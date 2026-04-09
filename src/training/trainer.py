"""
Training loop for AlphaZero-style chess network.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import torch
from torch.utils.data import DataLoader

from src.training.dataset import AlphaZeroDataset
from src.training.loss import alphazero_loss


@dataclass
class TrainerConfig:
    """
    Training hyperparameters.
    """
    batch_size: int = 64
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    num_epochs: int = 5
    shuffle: bool = True


@dataclass
class EpochStats:
    """
    Aggregate stats for one training epoch.
    """
    epoch: int
    total_loss: float
    policy_loss: float
    value_loss: float
    num_batches: int


class AlphaZeroTrainer:
    """
    Handles supervised training on self-play samples.
    """

    def __init__(
        self,
        model: torch.nn.Module,
        device: str = "cpu",
        config: TrainerConfig | None = None,
    ) -> None:
        self.model = model.to(device)
        self.device = torch.device(device)
        self.config = config or TrainerConfig()

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
        )

    def train_epoch(self, samples: List, epoch_number: int = 1) -> EpochStats:
        """
        Train model for one epoch on provided samples.
        """
        dataset = AlphaZeroDataset(samples)
        dataloader = DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=self.config.shuffle,
        )

        self.model.train()

        total_loss_sum = 0.0
        policy_loss_sum = 0.0
        value_loss_sum = 0.0
        num_batches = 0

        for states, policy_targets, value_targets in dataloader:
            states = states.to(self.device)
            policy_targets = policy_targets.to(self.device)
            value_targets = value_targets.to(self.device)

            self.optimizer.zero_grad()

            policy_logits, value_pred = self.model(states)
            loss, breakdown = alphazero_loss(
                policy_logits=policy_logits,
                value_pred=value_pred,
                policy_target=policy_targets,
                value_target=value_targets,
            )

            loss.backward()
            self.optimizer.step()

            total_loss_sum += breakdown.total_loss
            policy_loss_sum += breakdown.policy_loss
            value_loss_sum += breakdown.value_loss
            num_batches += 1

        if num_batches == 0:
            return EpochStats(
                epoch=epoch_number,
                total_loss=0.0,
                policy_loss=0.0,
                value_loss=0.0,
                num_batches=0,
            )

        return EpochStats(
            epoch=epoch_number,
            total_loss=total_loss_sum / num_batches,
            policy_loss=policy_loss_sum / num_batches,
            value_loss=value_loss_sum / num_batches,
            num_batches=num_batches,
        )

    def train(self, samples: List) -> list[EpochStats]:
        """
        Train for multiple epochs.
        """
        history: list[EpochStats] = []
        for epoch_idx in range(1, self.config.num_epochs + 1):
            stats = self.train_epoch(samples, epoch_number=epoch_idx)
            history.append(stats)
        return history
