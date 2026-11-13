"""
Replay buffer with atomic snapshots and an append-only per-game recovery journal.
"""

from __future__ import annotations

import os
import pickle
import random
import tempfile
from collections import deque
from pathlib import Path
from typing import Deque, Iterable, List
from uuid import uuid4

import numpy as np

from src.training.self_play import SelfPlaySample


class ReplayBuffer:
    """Fixed-size replay storage with crash-safe incremental game persistence."""

    def __init__(self, capacity: int = 50000) -> None:
        if capacity < 1:
            raise ValueError("Replay buffer capacity must be positive.")
        self.capacity = capacity
        self.buffer: Deque[SelfPlaySample] = deque(maxlen=capacity)
        self._pending_journal_files: set[str] = set()

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

    @staticmethod
    def _journal_directory(path: Path) -> Path:
        return path.parent / f"{path.stem}_journal"

    @staticmethod
    def _atomic_pickle(payload: object, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=destination.parent,
                prefix=f".{destination.name}.", suffix=".tmp", delete=False
            ) as handle:
                temp_name = handle.name
                pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, destination)
        finally:
            if temp_name and os.path.exists(temp_name):
                os.unlink(temp_name)

    def save_game(
        self,
        samples: Iterable[SelfPlaySample],
        snapshot_path: str | Path,
        iteration: int,
        game_number: int,
    ) -> None:
        """Persist only the new game's samples, not the entire replay buffer."""
        path = Path(snapshot_path)
        journal_dir = self._journal_directory(path)
        filename = (
            f"iteration_{iteration:04d}_game_{game_number:04d}_{uuid4().hex}.pkl"
        )
        self._atomic_pickle(list(samples), journal_dir / filename)
        self._pending_journal_files.add(filename)

    def save(self, path: str | Path) -> None:
        """Atomically snapshot the buffer and acknowledge journal chunks."""
        path = Path(path)
        payload = {
            "version": 2,
            "capacity": self.capacity,
            "samples": list(self.buffer),
            "journal_files": sorted(self._pending_journal_files),
        }
        self._atomic_pickle(payload, path)

        journal_dir = self._journal_directory(path)
        for filename in self._pending_journal_files:
            chunk = journal_dir / filename
            if chunk.exists():
                chunk.unlink()
        self._pending_journal_files.clear()

    @staticmethod
    def _upgrade_samples(items: list[SelfPlaySample]) -> list[SelfPlaySample]:
        upgraded = []
        for sample in items:
            state = np.asarray(sample.state, dtype=np.float32)
            if state.shape == (19, 8, 8):
                # Legacy 19-plane samples keep their original fullmove plane.
                state = np.concatenate(
                    [state, np.zeros((1, 8, 8), dtype=np.float32)], axis=0
                )
                sample.state = state
            elif state.shape != (20, 8, 8):
                raise ValueError(
                    f"Unsupported replay sample state shape {state.shape}; "
                    "expected (19, 8, 8) or (20, 8, 8)."
                )
            upgraded.append(sample)
        return upgraded

    def load(self, path: str | Path) -> None:
        """Restore a snapshot and replay every journal chunk not yet snapshotted."""
        path = Path(path)
        included_journal_files: set[str] = set()

        if path.is_file():
            with path.open("rb") as handle:
                payload = pickle.load(handle)

            if isinstance(payload, dict):
                if payload.get("version") not in (1, 2) or not isinstance(payload.get("samples"), list):
                    raise ValueError(f"Unsupported replay buffer format: {path}")
                items = payload["samples"]
                included_journal_files = set(payload.get("journal_files", []))
            elif isinstance(payload, list):
                # Legacy list-based snapshots.
                items = payload
            else:
                raise ValueError(f"Invalid replay buffer payload: {path}")
            self.buffer = deque(self._upgrade_samples(items), maxlen=self.capacity)

        journal_dir = self._journal_directory(path)
        if journal_dir.is_dir():
            for chunk_path in sorted(journal_dir.glob("*.pkl")):
                if chunk_path.name in included_journal_files:
                    chunk_path.unlink(missing_ok=True)
                    continue
                with chunk_path.open("rb") as handle:
                    chunk_samples = pickle.load(handle)
                if not isinstance(chunk_samples, list):
                    raise ValueError(f"Invalid replay journal chunk: {chunk_path}")
                self.buffer.extend(self._upgrade_samples(chunk_samples))
                self._pending_journal_files.add(chunk_path.name)
