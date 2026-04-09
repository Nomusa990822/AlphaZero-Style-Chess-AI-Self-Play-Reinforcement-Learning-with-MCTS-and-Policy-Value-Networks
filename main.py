"""
main.py

Quick smoke test for Stage 2 network.
"""

import chess
import torch

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet


def main() -> None:
    board = chess.Board()

    encoder = BoardEncoder()
    move_encoding = MoveEncoding()
    model = AlphaZeroNet(action_size=move_encoding.action_size)

    inference = ModelInference(
        model=model,
        move_encoding=move_encoding,
        encoder=encoder,
        device="cpu"
    )

    policy_probs, value = inference.predict(board)
    best_move = inference.best_legal_move(board)

    print("Board:")
    print(board)
    print("\nAction size:", move_encoding.action_size)
    print("Predicted value:", value)
    print("Best legal move:", best_move.uci() if best_move else None)
    print("Top probability sum:", float(policy_probs.sum()))


if __name__ == "__main__":
    main()
