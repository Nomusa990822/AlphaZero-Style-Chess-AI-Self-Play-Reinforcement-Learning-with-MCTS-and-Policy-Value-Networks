"""
Main ideas:
- maintain a current best model
- generate self-play games
- train a candidate model
- compare candidate vs current best
- promote candidate if it performs well enough
- log metrics and save checkpoints
"""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from typing import Any

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import checkpoint_exists, load_checkpoint, save_checkpoint
from src.training.evaluator import NetworkEvaluator
from src.training.metrics import IterationMetrics, MetricsLogger
from src.training.replay_buffer import ReplayBuffer
from src.training.self_play import SelfPlayGameResult, SelfPlayGenerator
from src.training.trainer import AlphaZeroTrainer, TrainerConfig


@dataclass
class PipelineConfig:
    """
    Outer-loop training configuration.
    """
    device: str = "cpu"
    replay_buffer_capacity: int = 20000

    iterations: int = 15
    self_play_games_per_iteration: int = 8
    self_play_max_moves: int = 300

    self_play_opening_temperature_moves: int = 15
    self_play_opening_temperature: float = 1.0
    self_play_late_temperature: float = 0.1

    self_play_resign_threshold: float = -0.9
    self_play_min_moves_before_resign: int = 20

    self_play_adjudicate_on_max_moves: bool = True
    self_play_adjudication_threshold: float = 0.25

    training_batch_size: int = 32
    training_epochs: int = 5
    learning_rate: float = 1e-3
    candidate_learning_rate: float = 5e-4
    weight_decay: float = 1e-4

    train_mcts_simulations: int = 40
    eval_mcts_simulations: int = 50

    train_dirichlet_alpha: float = 0.5
    train_dirichlet_epsilon: float = 0.30

    # Make evaluation less deterministic so differences can surface.
    eval_add_dirichlet_noise: bool = True
    eval_dirichlet_alpha: float = 0.3
    eval_dirichlet_epsilon: float = 0.25
    eval_temperature: float = 0.2

    gating_games: int = 10
    required_promotion_score: float = 0.52

    checkpoint_dir: str = "data/checkpoints"
    log_dir: str = "data/logs"
    replay_buffer_path: str = "data/replay_buffer/latest_buffer.pkl"
    best_model_checkpoint: str = "data/checkpoints/best_model.pt"
    latest_candidate_checkpoint: str = "data/checkpoints/latest_candidate.pt"

    resume_best_model: bool = True


class AlphaZeroPipeline:
    """
    Full iterative AlphaZero-style training pipeline.
    """

    def __init__(
        self,
        move_encoding: MoveEncoding,
        encoder: BoardEncoder,
        network_config: NetworkConfig,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        self.move_encoding = move_encoding
        self.encoder = encoder
        self.network_config = network_config
        self.config = pipeline_config or PipelineConfig()

        self.metrics_logger = MetricsLogger(self.config.log_dir)
        self.replay_buffer = ReplayBuffer(capacity=self.config.replay_buffer_capacity)

        self.best_model = AlphaZeroNet(
            action_size=self.move_encoding.action_size,
            config=self.network_config,
        )
        self.best_model.to(self.config.device)

        self.best_trainer = AlphaZeroTrainer(
            model=self.best_model,
            device=self.config.device,
            config=TrainerConfig(
                batch_size=self.config.training_batch_size,
                learning_rate=self.config.learning_rate,
                weight_decay=self.config.weight_decay,
                num_epochs=self.config.training_epochs,
                shuffle=True,
            ),
        )

        if self.config.resume_best_model and checkpoint_exists(self.config.best_model_checkpoint):
            load_checkpoint(
                self.config.best_model_checkpoint,
                self.best_model,
                optimizer=self.best_trainer.optimizer,
                map_location=self.config.device,
            )
            print(f"Loaded best model from {self.config.best_model_checkpoint}")

    def _make_inference(self, model: AlphaZeroNet) -> ModelInference:
        """
        Build inference wrapper for a model.
        """
        return ModelInference(
            model=model,
            move_encoding=self.move_encoding,
            encoder=self.encoder,
            device=self.config.device,
        )

    def _build_self_play_generator(self, inference: ModelInference) -> SelfPlayGenerator:
        """
        Build self-play generator for current best model.
        """
        return SelfPlayGenerator(
            inference=inference,
            move_encoding=self.move_encoding,
            encoder=self.encoder,
            mcts_config=MCTSConfig(
                num_simulations=self.config.train_mcts_simulations,
                c_puct=1.5,
                dirichlet_alpha=self.config.train_dirichlet_alpha,
                dirichlet_epsilon=self.config.train_dirichlet_epsilon,
                add_dirichlet_noise=True,
                temperature=1.0,
            ),
            max_moves=self.config.self_play_max_moves,
            opening_temperature_moves=self.config.self_play_opening_temperature_moves,
            opening_temperature=self.config.self_play_opening_temperature,
            late_temperature=self.config.self_play_late_temperature,
            resign_threshold=self.config.self_play_resign_threshold,
            min_moves_before_resign=self.config.self_play_min_moves_before_resign,
            adjudicate_on_max_moves=self.config.self_play_adjudicate_on_max_moves,
            adjudication_threshold=self.config.self_play_adjudication_threshold,
        )

    def _result_to_white_score(self, result: str) -> float:
        """
        Convert chess result to white score.
        """
        if result == "1-0":
            return 1.0
        if result == "0-1":
            return 0.0
        return 0.5

    def _collect_self_play_games(
        self,
        generator: SelfPlayGenerator,
        num_games: int,
    ) -> list[SelfPlayGameResult]:
        """
        Generate self-play games.
        """
        return generator.generate_games(num_games)

    def _build_candidate_model(self) -> tuple[AlphaZeroNet, AlphaZeroTrainer]:
        """
        Build candidate model initialized from current best weights.
        """
        candidate_model = AlphaZeroNet(
            action_size=self.move_encoding.action_size,
            config=self.network_config,
        )
        candidate_model.load_state_dict(copy.deepcopy(self.best_model.state_dict()))
        candidate_model.to(self.config.device)

        # Train the candidate more deliberately than the current best.
        candidate_trainer = AlphaZeroTrainer(
            model=candidate_model,
            device=self.config.device,
            config=TrainerConfig(
                batch_size=self.config.training_batch_size,
                learning_rate=self.config.candidate_learning_rate,
                weight_decay=self.config.weight_decay,
                num_epochs=self.config.training_epochs,
                shuffle=True,
            ),
        )
        return candidate_model, candidate_trainer

    def run_iteration(self, iteration: int) -> dict[str, Any]:
        """
        Run one outer training iteration.
        """
        print(f"\n{'=' * 80}")
        print(f"ITERATION {iteration}")
        print(f"{'=' * 80}")

        best_inference = self._make_inference(self.best_model)
        self_play_generator = self._build_self_play_generator(best_inference)

        print("Generating self-play games...")
        game_results = self._collect_self_play_games(
            self_play_generator,
            self.config.self_play_games_per_iteration,
        )

        total_positions = 0
        total_game_length = 0
        total_white_score = 0.0

        for idx, game_result in enumerate(game_results, start=1):
            self.replay_buffer.add_game(game_result.samples)
            total_positions += game_result.num_positions
            total_game_length += len(game_result.moves)
            total_white_score += self._result_to_white_score(game_result.result)

            ending_notes = []
            if game_result.ended_by_resignation:
                ending_notes.append("resign")
            if game_result.ended_by_adjudication:
                ending_notes.append("adjudicated")
            note_text = f" ({', '.join(ending_notes)})" if ending_notes else ""

            print(
                f"  Game {idx}: result={game_result.result}, "
                f"moves={len(game_result.moves)}, "
                f"samples={game_result.num_positions}{note_text}"
            )

        avg_game_length = total_game_length / max(1, len(game_results))
        avg_white_score = total_white_score / max(1, len(game_results))

        print(f"Replay buffer size: {len(self.replay_buffer)}")

        print("Building candidate model from best model...")
        candidate_model, candidate_trainer = self._build_candidate_model()

        print("Training candidate model...")
        train_history = candidate_trainer.train(list(self.replay_buffer.buffer))
        for epoch_stats in train_history:
            print(
                f"  Epoch {epoch_stats.epoch}: "
                f"total={epoch_stats.total_loss:.4f}, "
                f"policy={epoch_stats.policy_loss:.4f}, "
                f"value={epoch_stats.value_loss:.4f}, "
                f"batches={epoch_stats.num_batches}"
            )

        print("Saving latest candidate checkpoint...")
        save_checkpoint(
            self.config.latest_candidate_checkpoint,
            candidate_model,
            candidate_trainer.optimizer,
            epoch=train_history[-1].epoch if train_history else 0,
            extra={"iteration": iteration, "replay_buffer_size": len(self.replay_buffer)},
        )

        print("Evaluating candidate vs current best...")
        evaluator = NetworkEvaluator(
            move_encoding=self.move_encoding,
            mcts_config=MCTSConfig(
                num_simulations=self.config.eval_mcts_simulations,
                add_dirichlet_noise=self.config.eval_add_dirichlet_noise,
                dirichlet_alpha=self.config.eval_dirichlet_alpha,
                dirichlet_epsilon=self.config.eval_dirichlet_epsilon,
                temperature=self.config.eval_temperature,
            ),
        )

        candidate_inference = self._make_inference(candidate_model)
        should_promote, eval_result = evaluator.should_promote_candidate(
            candidate_inference=candidate_inference,
            best_inference=best_inference,
            num_games=self.config.gating_games,
            required_score=self.config.required_promotion_score,
        )

        print(
            f"Evaluation result: W={eval_result.wins}, "
            f"L={eval_result.losses}, D={eval_result.draws}, "
            f"Score={eval_result.score:.3f}"
        )

        if should_promote:
            print("Candidate promoted to BEST model.")
            self.best_model.load_state_dict(candidate_model.state_dict())
            save_checkpoint(
                self.config.best_model_checkpoint,
                self.best_model,
                self.best_trainer.optimizer,
                epoch=train_history[-1].epoch if train_history else 0,
                extra={"iteration": iteration, "promoted": True},
            )
        else:
            print("Candidate rejected. Keeping current BEST model.")

        final_epoch = train_history[-1] if train_history else None
        metrics = IterationMetrics(
            iteration=iteration,
            self_play_games=len(game_results),
            replay_buffer_size=len(self.replay_buffer),
            total_positions_generated=total_positions,
            average_game_length=avg_game_length,
            average_game_result_white_score=avg_white_score,
            training_epochs=self.config.training_epochs,
            final_total_loss=final_epoch.total_loss if final_epoch else 0.0,
            final_policy_loss=final_epoch.policy_loss if final_epoch else 0.0,
            final_value_loss=final_epoch.value_loss if final_epoch else 0.0,
            evaluation_games=eval_result.games_played,
            evaluation_wins=eval_result.wins,
            evaluation_losses=eval_result.losses,
            evaluation_draws=eval_result.draws,
            evaluation_score=eval_result.score,
            model_promoted=should_promote,
        )

        self.metrics_logger.append_iteration_metrics(metrics)
        self.metrics_logger.save_json_summary(
            {
                "iteration": iteration,
                "metrics": asdict(metrics),
                "evaluation_result": {
                    "wins": eval_result.wins,
                    "losses": eval_result.losses,
                    "draws": eval_result.draws,
                    "games_played": eval_result.games_played,
                    "score": eval_result.score,
                },
            },
            filename=f"iteration_{iteration:03d}_summary.json",
        )

        return {
            "iteration": iteration,
            "metrics": metrics,
            "evaluation_result": eval_result,
            "promoted": should_promote,
        }

    def run(self) -> list[dict[str, Any]]:
        """
        Run the full outer-loop training pipeline.
        """
        results: list[dict[str, Any]] = []

        for iteration in range(1, self.config.iterations + 1):
            result = self.run_iteration(iteration)
            results.append(result)

        return results
