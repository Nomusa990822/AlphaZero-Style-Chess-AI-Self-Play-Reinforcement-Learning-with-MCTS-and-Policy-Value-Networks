"""
Save and load training checkpoints.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch


def save_checkpoint(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    extra: dict[str, Any] | None = None,
) -> None:
    """
    Save training checkpoint.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "extra": extra or {},
    }
    torch.save(payload, path)


def load_checkpoint(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    map_location: str = "cpu",
) -> dict[str, Any]:
    """
    Load training checkpoint.

    Returns:
        Loaded payload
    """
    payload = torch.load(path, map_location=map_location)

    model.load_state_dict(payload["model_state_dict"])

    if optimizer is not None:
        optimizer.load_state_dict(payload["optimizer_state_dict"])

    return payload
