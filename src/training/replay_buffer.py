"""
Replay buffer for AlphaZero-style training data.
"""

from __future__ import annotations

import os
import pickle
import random
import tempfile
from collections import deque
from collections.abc import Iterable
from pathlib import Path
from typing import Deque, List

from src.training.self_play import SelfPlaySample


class ReplayBuffer:
    """Fixed-size replay buffer with atomic on-disk persistence."""

    def __init__(self, capacity: int = 50000) -> None:
        if capacity < 1:
            raise ValueError("Replay buffer capacity must be positive.")
        self.capacity = capacity
        self.buffer: Deque[SelfPlaySample] = deque(maxlen=capacity)

    def __len__(self) -> int:
        return len(self.buffer)

    def add_sample(self, sample: SelfPlaySample) -> None:
        self.buffer.append(sample)

    def add_game(self, samples: Iterable[SelfPlaySample]) -> None:
        self.buffer.extend(samples)

    def sample_batch(self, batch_size: int) -> List[SelfPlaySample]:
        if batch_size < 1:
            raise ValueError("batch_size must be positive.")
        if batch_size > len(self.buffer):
            raise ValueError(
                f"Requested batch_size={batch_size}, but buffer only has {len(self.buffer)} samples."
            )
        return random.sample(list(self.buffer), batch_size)

    def save(self, path: str | Path) -> None:
        """Write a complete snapshot then atomically replace the previous one."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=path.parent, prefix=f".{path.name}.",
                suffix=".tmp", delete=False
            ) as handle:
                temp_name = handle.name
                pickle.dump(
                    {"version": 1, "capacity": self.capacity, "samples": list(self.buffer)},
                    handle,
                    protocol=pickle.HIGHEST_PROTOCOL,
                )
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
        finally:
            if temp_name and os.path.exists(temp_name):
                os.unlink(temp_name)

    def load(self, path: str | Path) -> None:
        """Load current versioned snapshots and legacy list-based buffers."""
        path = Path(path)
        with path.open("rb") as handle:
            payload = pickle.load(handle)

        if isinstance(payload, dict):
            if payload.get("version") != 1 or not isinstance(payload.get("samples"), list):
                raise ValueError(f"Unsupported replay buffer format: {path}")
            items = payload["samples"]
        elif isinstance(payload, list):
            items = payload
        else:
            raise ValueError(f"Invalid replay buffer payload: {path}")

        self.buffer = deque(items, maxlen=self.capacity)
