"""
Defines a standard residual block for the AlphaZero-style chess network.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class ResidualBlock(nn.Module):
    """
    Standard 2-layer residual block with BatchNorm and ReLU.

    Input shape:
        (batch_size, channels, 8, 8)

    Output shape:
        (batch_size, channels, 8, 8)
    """

    def __init__(self, channels: int) -> None:
        """
        Args:
            channels: Number of input/output feature channels.
        """
        super().__init__()

        self.conv1 = nn.Conv2d(
            in_channels=channels,
            out_channels=channels,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=False
        )
        self.bn1 = nn.BatchNorm2d(channels)

        self.conv2 = nn.Conv2d(
            in_channels=channels,
            out_channels=channels,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=False
        )
        self.bn2 = nn.BatchNorm2d(channels)

        self.relu = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through residual block.

        Args:
            x: Tensor of shape (B, C, 8, 8)

        Returns:
            Tensor of shape (B, C, 8, 8)
        """
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        out = out + identity
        out = self.relu(out)

        return out
