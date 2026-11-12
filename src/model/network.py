"""
Main AlphaZero-style policy-value network for chess.

This network:
- accepts encoded board tensors of shape (B, 20, 8, 8)
- processes them through an initial convolution block
- applies residual blocks
- outputs:
    1. policy logits over action space
    2. scalar value in [-1, 1]
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn

from src.model.policy_head import PolicyHead
from src.model.residual_block import ResidualBlock
from src.model.value_head import ValueHead


@dataclass
class NetworkConfig:
    """
    Configuration for AlphaZero-style chess network.
    """
    input_channels: int = 20
    board_size: int = 8
    num_filters: int = 128
    num_res_blocks: int = 6
    value_hidden_size: int = 256
    policy_head_channels: int = 2
    value_head_channels: int = 1


class AlphaZeroNet(nn.Module):
    """
    AlphaZero-style policy-value network for chess.
    """

    def __init__(self, action_size: int, config: NetworkConfig | None = None) -> None:
        """
        Args:
            action_size: Total size of the move action space.
            config: Optional network configuration.
        """
        super().__init__()

        self.config = config or NetworkConfig()
        self.action_size = action_size

        self.input_block = nn.Sequential(
            nn.Conv2d(
                in_channels=self.config.input_channels,
                out_channels=self.config.num_filters,
                kernel_size=3,
                stride=1,
                padding=1,
                bias=False
            ),
            nn.BatchNorm2d(self.config.num_filters),
            nn.ReLU(inplace=True),
        )

        self.res_blocks = nn.Sequential(
            *[ResidualBlock(self.config.num_filters) for _ in range(self.config.num_res_blocks)]
        )

        self.policy_head = PolicyHead(
            in_channels=self.config.num_filters,
            board_size=self.config.board_size,
            action_size=action_size,
            head_channels=self.config.policy_head_channels,
        )

        self.value_head = ValueHead(
            in_channels=self.config.num_filters,
            board_size=self.config.board_size,
            hidden_size=self.config.value_hidden_size,
            head_channels=self.config.value_head_channels,
        )

        self._initialize_weights()

    def _initialize_weights(self) -> None:
        """
        Initialize weights using Kaiming initialization where appropriate.
        """
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, nonlinearity="relu")
            elif isinstance(module, nn.Linear):
                nn.init.kaiming_normal_(module.weight, nonlinearity="relu")
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.BatchNorm2d):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.

        Args:
            x: Input tensor of shape (B, 20, 8, 8)

        Returns:
            policy_logits: Tensor of shape (B, action_size)
            value: Tensor of shape (B, 1)
        """
        features = self.input_block(x)
        features = self.res_blocks(features)

        policy_logits = self.policy_head(features)
        value = self.value_head(features)

        return policy_logits, value

    def predict(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Inference helper with eval mode and no gradient tracking.

        Args:
            x: Input tensor of shape (B, 20, 8, 8)

        Returns:
            policy_probs: Tensor of shape (B, action_size)
            value: Tensor of shape (B, 1)
        """
        self.eval()
        with torch.no_grad():
            policy_logits, value = self.forward(x)
            policy_probs = torch.softmax(policy_logits, dim=1)
        return policy_probs, value
