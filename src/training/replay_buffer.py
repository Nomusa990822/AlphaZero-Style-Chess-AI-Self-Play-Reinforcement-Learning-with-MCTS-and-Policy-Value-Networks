"""
Replay buffer for AlphaZero-style training data.
"""

from __future__ import annotations

import pickle
import random
from collections import deque
from pathlib import Path
from typing import Deque, List

from src.training.self_play import SelfPlaySample


class ReplayBuffer:
    """
    Fixed-size replay buffer for self-play samples.
    """

    def __init__(self, capacity: int = 50000) -> None:
        self.capacity = capacity
        self.buffer: Deque[SelfPlaySample] = deque(maxlen=capacity)

    def __len__(self) -> int:
        return len(self.buffer)

    def add_sample(self, sample: SelfPlaySample) -> None:
        self.buffer.append(sample)

    def add_game(self, samples: List[SelfPlaySample]) -> None:
        self.buffer.extend(samples)

    def sample_batch(self, batch_size: int) -> List[SelfPlaySample]:
        if batch_size > len(self.buffer):
            raise ValueError(
                f"Requested batch_size={batch_size}, but buffer only has {len(self.buffer)} samples."
            )
        return random.sample(list(self.buffer), batch_size)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "wb") as f:
            pickle.dump(list(self.buffer), f)

    def load(self, path: str | Path) -> None:
        path = Path(path)
        with open(path, "rb") as f:
            items = pickle.load(f)

        self.buffer = deque(items, maxlen=self.capacity)
