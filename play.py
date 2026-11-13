"""
Play terminal chess against the AlphaZero-style AI.
"""

from __future__ import annotations

import argparse

import chess

from src.agents.human_agent import HumanAgent
from src.agents.mcts_agent import MCTSAgent
from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import checkpoint_exists, load_checkpoint


PIECE_SYMBOLS = {
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
    ".": "·",
}


def render_board(board: chess.Board) -> str:
    """
    Pretty unicode terminal board.
    """
    rows = str(board).split("\n")
    rendered = []
    for rank_idx, row in enumerate(rows):
        rank_label = 8 - rank_idx
        pieces = row.split(" ")
        rendered_row = " ".join(PIECE_SYMBOLS.get(piece, piece) for piece in pieces)
        rendered.append(f"{rank_label}  {rendered_row}")
    rendered.append("\n   a b c d e f g h")
    return "\n".join(rendered)


def describe_result(result: str) -> str:
    """
    Human-readable result string.
    """
    if result == "1-0":
        return "White wins"
    if result == "0-1":
        return "Black wins"
    return "Draw"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play terminal chess against the AI.")
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="data/checkpoints/best_model.pt",
        help="Path to model checkpoint.",
    )
    parser.add_argument(
        "--human-color",
        type=str,
        choices=["white", "black"],
        default="white",
        help="Choose whether the human plays White or Black.",
    )
    parser.add_argument(
        "--simulations",
        type=int,
        default=50,
        help="Number of MCTS simulations per AI move.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    board = chess.Board()
    human = HumanAgent()

    move_encoding = MoveEncoding()
    encoder = BoardEncoder()

    model = AlphaZeroNet(
        action_size=move_encoding.action_size,
        config=NetworkConfig(
            input_channels=20,
            board_size=8,
            num_filters=64,
            num_res_blocks=3,
            value_hidden_size=128,
        ),
    )

    if checkpoint_exists(args.checkpoint):
        load_checkpoint(args.checkpoint, model, optimizer=None, map_location="cpu")
        print(f"Loaded checkpoint: {args.checkpoint}")
    else:
        print("No checkpoint found. Using untrained model.")

    inference = ModelInference(
        model=model,
        move_encoding=move_encoding,
        encoder=encoder,
        device="cpu",
    )

    ai_agent = MCTSAgent(
        inference=inference,
        move_encoding=move_encoding,
        mcts_config=MCTSConfig(
            num_simulations=args.simulations,
            c_puct=1.5,
            add_dirichlet_noise=False,
            temperature=0.0,
        ),
    )

    human_is_white = args.human_color == "white"

    print("\nStarting game.")
    print(f"Human plays: {'White' if human_is_white else 'Black'}")
    print("Enter moves in UCI format like e2e4 or e7e8q.")
    print("Type 'quit' or 'exit' to leave.\n")

    try:
        while not board.is_game_over():
            print(render_board(board))
            print()

            if (board.turn == chess.WHITE and human_is_white) or (
                board.turn == chess.BLACK and not human_is_white
            ):
                print("Your turn.")
                move = human.choose_move(board)
            else:
                print("AI thinking...")
                move = ai_agent.choose_move(board, temperature=0.0)
                print(f"AI plays: {move.uci()}")

            board.push(move)
            print("-" * 40)

        print(render_board(board))
        result = board.result(claim_draw=True)
        print(f"\nGame over: {describe_result(result)} ({result})")

    except KeyboardInterrupt:
        print("\nGame exited.")
        return


if __name__ == "__main__":
    main()
