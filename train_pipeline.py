"""
train_pipeline.py

Stage 5 iterative training entry point.
"""

from __future__ import annotations

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.model.network import NetworkConfig
from src.training.pipeline import AlphaZeroPipeline, PipelineConfig


def main() -> None:
    move_encoding = MoveEncoding()
    encoder = BoardEncoder()

    network_config = NetworkConfig(
        input_channels=19,
        board_size=8,
        num_filters=64,
        num_res_blocks=3,
        value_hidden_size=128,
    )

    pipeline_config = PipelineConfig(
    device="cpu",
    replay_buffer_capacity=20000,

    iterations=15,
    self_play_games_per_iteration=8,
    self_play_max_moves=1000,

    self_play_opening_temperature_moves=15,
    self_play_opening_temperature=1.0,
    self_play_late_temperature=0.1,

    self_play_resign_threshold=-0.85,
    self_play_min_moves_before_resign=20,

    self_play_adjudicate_on_max_moves=True,
    self_play_adjudication_threshold=0.15,

    training_batch_size=32,
    training_epochs=5,
    learning_rate=1e-3,
    candidate_learning_rate=5e-4,
    weight_decay=1e-4,

    train_mcts_simulations=40,
    eval_mcts_simulations=50,

    train_dirichlet_alpha=0.5,
    train_dirichlet_epsilon=0.30,

    eval_add_dirichlet_noise=True,
    eval_dirichlet_alpha=0.3,
    eval_dirichlet_epsilon=0.25,
    eval_temperature=0.2,

    gating_games=10,
    required_promotion_score=0.52,

    checkpoint_dir="data/checkpoints",
    log_dir="data/logs",
    replay_buffer_path="data/replay_buffer/latest_buffer.pkl",
    best_model_checkpoint="data/checkpoints/best_model.pt",
    latest_candidate_checkpoint="data/checkpoints/latest_candidate.pt",

    resume_best_model=True,
    )

    pipeline = AlphaZeroPipeline(
        move_encoding=move_encoding,
        encoder=encoder,
        network_config=network_config,
        pipeline_config=pipeline_config,
    )

    results = pipeline.run()

    print("\nTraining complete.")
    print(f"Total iterations run: {len(results)}")


if __name__ == "__main__":
    main()
