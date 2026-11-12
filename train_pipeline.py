"""
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
        device="auto",
        replay_buffer_capacity=20000,

        iterations=2,
        self_play_games_per_iteration=40,
        self_play_max_moves=250,

        self_play_opening_temperature_moves=30,
        self_play_opening_temperature=1.3,
        self_play_late_temperature=0.5,

        # Keep resignation disabled for now.
        self_play_resign_threshold=None,
        self_play_min_moves_before_resign=30,

        self_play_adjudicate_on_max_moves=True,
        self_play_adjudication_threshold=0.00,

        training_batch_size=32,
        training_epochs=10,
        learning_rate=1e-3,
        candidate_learning_rate=2e-4,
        weight_decay=1e-4,

        train_mcts_simulations=80,
        eval_mcts_simulations=100,

        train_dirichlet_alpha=0.5,
        train_dirichlet_epsilon=0.30,

        eval_add_dirichlet_noise=True,
        eval_dirichlet_alpha=0.3,
        eval_dirichlet_epsilon=0.25,
        eval_temperature=0.5,

        gating_games=24,
        required_promotion_score=0.55,

        checkpoint_dir="data/checkpoints",
        log_dir="data/logs",
        replay_buffer_path="data/replay_buffer/latest_buffer.pkl",
        best_model_checkpoint="data/checkpoints/best_model.pt",
        latest_candidate_checkpoint="data/checkpoints/latest_candidate.pt",

        resume_best_model=True,
    )

    print("Pipeline config:")
    print(f"  iterations={pipeline_config.iterations}")
    print(f"  self_play_games_per_iteration={pipeline_config.self_play_games_per_iteration}")
    print(f"  self_play_max_moves={pipeline_config.self_play_max_moves}")
    print(f"  self_play_opening_temperature_moves={pipeline_config.self_play_opening_temperature_moves}")
    print(f"  self_play_opening_temperature={pipeline_config.self_play_opening_temperature}")
    print(f"  self_play_late_temperature={pipeline_config.self_play_late_temperature}")
    print(f"  self_play_resign_threshold={pipeline_config.self_play_resign_threshold}")
    print(f"  self_play_min_moves_before_resign={pipeline_config.self_play_min_moves_before_resign}")
    print(f"  self_play_adjudicate_on_max_moves={pipeline_config.self_play_adjudicate_on_max_moves}")
    print(f"  self_play_adjudication_threshold={pipeline_config.self_play_adjudication_threshold}")
    print(f"  replay_buffer_capacity={pipeline_config.replay_buffer_capacity}")
    print(f"  training_batch_size={pipeline_config.training_batch_size}")
    print(f"  training_epochs={pipeline_config.training_epochs}")
    print(f"  learning_rate={pipeline_config.learning_rate}")
    print(f"  candidate_learning_rate={pipeline_config.candidate_learning_rate}")
    print(f"  train_mcts_simulations={pipeline_config.train_mcts_simulations}")
    print(f"  eval_mcts_simulations={pipeline_config.eval_mcts_simulations}")
    print(f"  eval_add_dirichlet_noise={pipeline_config.eval_add_dirichlet_noise}")
    print(f"  eval_dirichlet_alpha={pipeline_config.eval_dirichlet_alpha}")
    print(f"  eval_dirichlet_epsilon={pipeline_config.eval_dirichlet_epsilon}")
    print(f"  eval_temperature={pipeline_config.eval_temperature}")
    print(f"  gating_games={pipeline_config.gating_games}")
    print(f"  required_promotion_score={pipeline_config.required_promotion_score}")
    print(f"  resume_best_model={pipeline_config.resume_best_model}")

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
