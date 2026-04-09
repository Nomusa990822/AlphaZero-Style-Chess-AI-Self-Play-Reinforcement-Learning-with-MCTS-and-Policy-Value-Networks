"""
PyTorch dataset for AlphaZero self-play samples.
"""

from __future__ import annotations

from typing import List

import numpy as np
import torch
from torch.utils.data import Dataset

from src.training.self_play import SelfPlaySample


class AlphaZeroDataset(Dataset):
    """
    Dataset wrapper around self-play samples.
    """

    def __init__(self, samples: List[SelfPlaySample]) -> None:
        self.samples = samples

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        sample = self.samples[idx]

        state = torch.tensor(sample.state, dtype=torch.float32)
        policy_target = torch.tensor(sample.policy_target, dtype=torch.float32)
        value_target = torch.tensor([sample.value_target], dtype=torch.float32)

        return state, policy_target, value_target
