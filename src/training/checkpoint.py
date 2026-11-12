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
        "format_version": 2,
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
        with open(temp_name, "rb+") as handle:
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

    saved_state = payload["model_state_dict"]
    current_state = model.state_dict()
    migrated_input_channels = False

    for key, saved_tensor in list(saved_state.items()):
        if key not in current_state or saved_tensor.shape == current_state[key].shape:
            continue
        current_tensor = current_state[key]
        if (
            key == "input_block.0.weight"
            and saved_tensor.ndim == 4
            and current_tensor.ndim == 4
            and saved_tensor.shape[0] == current_tensor.shape[0]
            and saved_tensor.shape[1] == 19
            and current_tensor.shape[1] == 20
            and saved_tensor.shape[2:] == current_tensor.shape[2:]
        ):
            migrated = torch.zeros_like(current_tensor)
            migrated[:, :19] = saved_tensor
            saved_state[key] = migrated
            migrated_input_channels = True
        else:
            raise RuntimeError(
                f"Checkpoint tensor shape mismatch for {key}: "
                f"saved={tuple(saved_tensor.shape)}, "
                f"model={tuple(current_tensor.shape)}"
            )

    model.load_state_dict(saved_state)

    optimizer_state = payload.get("optimizer_state_dict")
    if optimizer is not None and optimizer_state is not None and not migrated_input_channels:
        optimizer.load_state_dict(optimizer_state)
    elif migrated_input_channels:
        payload.setdefault("extra", {})["optimizer_state_reset_for_encoder_migration"] = True
        print(
            "Migrated checkpoint from 19 to 20 input planes. "
            "The optimizer state was reset because its first-layer tensors "
            "use the old shape."
        )

    return payload


def checkpoint_exists(path: str | Path) -> bool:
    """Check whether a checkpoint path exists."""
    return Path(path).exists()
