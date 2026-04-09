"""
End-to-end Stage 4 training pipeline for AlphaZero-style chess AI.

Flow:
1. initialize network
2. generate self-play games
3. store samples in replay buffer
4. train model
5. save checkpoint
"""

from __future__ import annotations

from pathlib import Path

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import save_checkpoint
from src.training.replay_buffer import ReplayBuffer
from src.training.self_play import SelfPlayGenerator
from src.training.trainer import AlphaZeroTrainer, TrainerConfig


def main() -> None:
    device = "cpu"

    move_encoding = MoveEncoding()
    encoder = BoardEncoder()

    model = AlphaZeroNet(
        action_size=move_encoding.action_size,
        config=NetworkConfig(
            input_channels=19,
            board_size=8,
            num_filters=64,
            num_res_blocks=3,
            value_hidden_size=128,
        ),
    )

    inference = ModelInference(
        model=model,
        move_encoding=move_encoding,
        encoder=encoder,
        device=device,
    )

    self_play = SelfPlayGenerator(
        inference=inference,
        move_encoding=move_encoding,
        encoder=encoder,
        mcts_config=MCTSConfig(
            num_simulations=20,
            c_puct=1.5,
            add_dirichlet_noise=True,
            temperature=1.0,
        ),
        max_moves=100,
        temperature_moves=12,
    )

    replay_buffer = ReplayBuffer(capacity=10000)

    print("Generating self-play games...")
    game_results = self_play.generate_games(num_games=2)

    for idx, game_result in enumerate(game_results, start=1):
        replay_buffer.add_game(game_result.samples)
        print(
            f"Game {idx}: result={game_result.result}, "
            f"moves={len(game_result.moves)}, "
            f"samples={len(game_result.samples)}"
        )

    print(f"\nReplay buffer size: {len(replay_buffer)}")

    trainer = AlphaZeroTrainer(
        model=model,
        device=device,
        config=TrainerConfig(
            batch_size=16,
            learning_rate=1e-3,
            weight_decay=1e-4,
            num_epochs=2,
            shuffle=True,
        ),
    )

    if len(replay_buffer) == 0:
        print("No samples collected. Exiting.")
        return

    print("\nTraining model...")
    history = trainer.train(list(replay_buffer.buffer))

    for stats in history:
        print(
            f"Epoch {stats.epoch}: "
            f"total_loss={stats.total_loss:.4f}, "
            f"policy_loss={stats.policy_loss:.4f}, "
            f"value_loss={stats.value_loss:.4f}, "
            f"batches={stats.num_batches}"
        )

    checkpoint_path = Path("data/checkpoints/stage4_latest.pt")
    save_checkpoint(
        path=checkpoint_path,
        model=model,
        optimizer=trainer.optimizer,
        epoch=history[-1].epoch if history else 0,
        extra={"replay_buffer_size": len(replay_buffer)},
    )

    print(f"\nCheckpoint saved to: {checkpoint_path}")


if __name__ == "__main__":
    main()
