"""
Value head for AlphaZero-style chess network.

Predicts a scalar value in [-1, 1] for the current position.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class ValueHead(nn.Module):
    """
    Value head that predicts a scalar evaluation.

    Architecture:
    - 1x1 convolution
    - batch norm
    - ReLU
    - flatten
    - fully connected hidden layer
    - fully connected output layer
    - tanh
    """

    def __init__(
        self,
        in_channels: int,
        board_size: int,
        hidden_size: int = 256,
        head_channels: int = 1
    ) -> None:
        """
        Args:
            in_channels: Number of channels from backbone.
            board_size: Board height/width (8 for chess).
            hidden_size: Hidden layer size.
            head_channels: Intermediate channel count for value head.
        """
        super().__init__()

        self.conv = nn.Conv2d(
            in_channels=in_channels,
            out_channels=head_channels,
            kernel_size=1,
            stride=1,
            padding=0,
            bias=False
        )
        self.bn = nn.BatchNorm2d(head_channels)
        self.relu = nn.ReLU(inplace=True)

        flattened_size = head_channels * board_size * board_size

        self.fc1 = nn.Linear(flattened_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, 1)
        self.tanh = nn.Tanh()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape (B, C, 8, 8)

        Returns:
            Value tensor of shape (B, 1), bounded to [-1, 1]
        """
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)

        x = torch.flatten(x, start_dim=1)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.tanh(x)

        return x
