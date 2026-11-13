"""
Inference helper utilities for AlphaZero-style chess network.
"""

from __future__ import annotations

from typing import Tuple

import chess
import numpy as np
import torch

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.model.network import AlphaZeroNet


class ModelInference:
    """
    Wraps board encoding + model inference + move decoding.
    """

    def __init__(
        self,
        model: AlphaZeroNet,
        move_encoding: MoveEncoding,
        encoder: BoardEncoder | None = None,
        device: str | torch.device = "cpu"
    ) -> None:
        """
        Args:
            model: Trained or untrained AlphaZero-style model.
            move_encoding: Move encoding helper.
            encoder: Optional board encoder instance.
            device: Torch device.
        """
        self.model = model.to(device)
        self.move_encoding = move_encoding
        self.encoder = encoder or BoardEncoder()
        self.device = torch.device(device)

    def board_to_tensor(self, board: chess.Board) -> torch.Tensor:
        """
        Encode a single board into a model-ready tensor.

        Args:
            board: python-chess board

        Returns:
            Tensor of shape (1, 20, 8, 8)
        """
        encoded = self.encoder.encode(board)
        tensor = torch.from_numpy(encoded).float().unsqueeze(0).to(self.device)
        return tensor

    def predict(self, board: chess.Board) -> Tuple[np.ndarray, float]:
        """
        Run inference on a single board.

        Args:
            board: python-chess board

        Returns:
            policy_probs: NumPy array of shape (action_size,)
            value: float scalar in [-1, 1]
        """
        input_tensor = self.board_to_tensor(board)
        policy_probs, value = self.model.predict(input_tensor)

        policy_probs_np = policy_probs.squeeze(0).detach().cpu().numpy()
        value_scalar = float(value.squeeze(0).item())

        return policy_probs_np, value_scalar

    def best_legal_move(self, board: chess.Board) -> chess.Move | None:
        """
        Choose the legal move with highest policy probability.

        Args:
            board: python-chess board

        Returns:
            Best legal move or None if no legal moves exist.
        """
        policy_probs, _ = self.predict(board)
        return self.move_encoding.decode_best_legal_move(policy_probs.tolist(), board)
