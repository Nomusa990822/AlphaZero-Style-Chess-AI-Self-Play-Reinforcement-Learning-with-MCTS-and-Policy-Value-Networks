"""
Policy head for AlphaZero-style chess network.

Maps shared trunk features into logits over the full action space.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class PolicyHead(nn.Module):
    """
    Policy head that predicts logits over all possible moves.

    Architecture:
    - 1x1 convolution
    - batch norm
    - ReLU
    - flatten
    - linear layer -> action logits
    """

    def __init__(
        self,
        in_channels: int,
        board_size: int,
        action_size: int,
        head_channels: int = 2
    ) -> None:
        """
        Args:
            in_channels: Number of channels from backbone.
            board_size: Board height/width (8 for chess).
            action_size: Size of move action space.
            head_channels: Intermediate channel count for policy head.
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
        self.fc = nn.Linear(flattened_size, action_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape (B, C, 8, 8)

        Returns:
            Policy logits of shape (B, action_size)
        """
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)

        x = torch.flatten(x, start_dim=1)
        x = self.fc(x)
        return x
