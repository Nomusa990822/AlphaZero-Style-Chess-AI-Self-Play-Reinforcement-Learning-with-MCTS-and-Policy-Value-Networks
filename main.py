"""
Quick smoke test for Stage 3 MCTS.
"""

import chess

from src.agents.mcts_agent import MCTSAgent
from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
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
        device="cpu",
    )

    agent = MCTSAgent(
        inference=inference,
        move_encoding=move_encoding,
        mcts_config=MCTSConfig(
            num_simulations=50,
            c_puct=1.5,
            add_dirichlet_noise=False,
            temperature=0.0,
        ),
    )

    move = agent.choose_move(board)

    print("Initial board:")
    print(board)
    print("\nChosen move from MCTS:", move.uci())


if __name__ == "__main__":
    main()
