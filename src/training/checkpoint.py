"""
Save and load training checkpoints.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import torch


def save_checkpoint(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None,
    epoch: int,
    extra: dict[str, Any] | None = None,
) -> None:
    """Save a checkpoint atomically to avoid corrupting the last good copy."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict() if optimizer is not None else None,
        "extra": extra or {},
    }

    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            temp_name = handle.name
        torch.save(payload, temp_name)
        with open(temp_name, "rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def load_checkpoint(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    map_location: str | torch.device = "cpu",
) -> dict[str, Any]:
    """Load a checkpoint and restore model and optional optimizer state."""
    payload = torch.load(path, map_location=map_location)

    model.load_state_dict(payload["model_state_dict"])

    optimizer_state = payload.get("optimizer_state_dict")
    if optimizer is not None and optimizer_state is not None:
        optimizer.load_state_dict(optimizer_state)

    return payload


def checkpoint_exists(path: str | Path) -> bool:
    """Check whether a checkpoint path exists."""
    return Path(path).exists()
