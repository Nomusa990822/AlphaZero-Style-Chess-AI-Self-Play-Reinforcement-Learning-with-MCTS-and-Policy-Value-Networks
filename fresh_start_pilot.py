"""Run a deliberately small, fresh-from-random CPU training pilot.

This is a pipeline smoke pilot, not a claim of playing strength. It creates an
explicitly labelled random baseline checkpoint, then runs one bounded iteration.
"""
from __future__ import annotations

from pathlib import Path

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import save_checkpoint
from src.training.pipeline import AlphaZeroPipeline, PipelineConfig
from src.training.trainer import AlphaZeroTrainer, TrainerConfig


def build_pilot_config() -> tuple[MoveEncoding, BoardEncoder, NetworkConfig, PipelineConfig]:
    move_encoding = MoveEncoding()
    encoder = BoardEncoder()
    network_config = NetworkConfig(
        input_channels=20,
        board_size=8,
        num_filters=64,
        num_res_blocks=3,
        value_hidden_size=128,
    )
    config = PipelineConfig(
        device="cpu",
        replay_buffer_capacity=2000,
        iterations=1,
        self_play_games_per_iteration=4,
        self_play_max_moves=80,
        self_play_opening_temperature_moves=20,
        self_play_opening_temperature=1.3,
        self_play_late_temperature=0.5,
        self_play_resign_threshold=None,
        self_play_min_moves_before_resign=30,
        self_play_adjudicate_on_max_moves=True,
        training_batch_size=32,
        training_epochs=1,
        learning_rate=1e-3,
        candidate_learning_rate=2e-4,
        weight_decay=1e-4,
        train_mcts_simulations=8,
        eval_mcts_simulations=8,
        train_dirichlet_alpha=0.5,
        train_dirichlet_epsilon=0.30,
        eval_add_dirichlet_noise=False,
        eval_temperature=0.0,
        gating_games=2,
        required_promotion_score=0.50,
        checkpoint_dir="data/checkpoints/fresh_pilot",
        log_dir="data/logs/fresh_pilot",
        replay_buffer_path="data/replay_buffer/fresh_pilot/replay.pkl",
        best_model_checkpoint="data/checkpoints/fresh_pilot/best_model.pt",
        latest_candidate_checkpoint="data/checkpoints/fresh_pilot/latest_candidate.pt",
        # We explicitly create and label a random baseline before pipeline startup.
        resume_best_model=True,
    )
    return move_encoding, encoder, network_config, config


def main() -> None:
    move_encoding, encoder, network_config, config = build_pilot_config()
    checkpoint = Path(config.best_model_checkpoint)
    if checkpoint.exists():
        raise FileExistsError(
            f"Refusing to overwrite an existing pilot baseline: {checkpoint}"
        )

    baseline = AlphaZeroNet(
        action_size=move_encoding.action_size,
        config=network_config,
    )
    baseline_trainer = AlphaZeroTrainer(
        model=baseline,
        device="cpu",
        config=TrainerConfig(
            batch_size=config.training_batch_size,
            learning_rate=config.learning_rate,
            weight_decay=config.weight_decay,
            num_epochs=config.training_epochs,
            shuffle=True,
        ),
    )
    save_checkpoint(
        checkpoint,
        baseline,
        baseline_trainer.optimizer,
        epoch=0,
        extra={
            "run_type": "fresh_start_smoke_pilot",
            "training_state": "random_initialization_baseline",
            "playing_strength_claim": False,
        },
    )
    print("Created explicitly labelled random-initialisation baseline.")
    print("Pilot limits: 1 iteration, 4 self-play games, 80-ply cap, 8 MCTS simulations.")
    print("This pilot is for pipeline validation, not playing-strength measurement.")

    pipeline = AlphaZeroPipeline(
        move_encoding=move_encoding,
        encoder=encoder,
        network_config=network_config,
        pipeline_config=config,
    )
    results = pipeline.run()
    print(f"Fresh-start pilot finished: {len(results)} iteration(s).")


if __name__ == "__main__":
    main()
