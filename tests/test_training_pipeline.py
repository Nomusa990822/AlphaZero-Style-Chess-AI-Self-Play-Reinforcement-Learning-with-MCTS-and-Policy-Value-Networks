import chess
import numpy as np
import pickle
import json
import torch

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import load_checkpoint
from src.training.dataset import AlphaZeroDataset
from src.training.loss import alphazero_loss
from src.training.metrics import MetricsLogger
from src.training.pipeline import AlphaZeroPipeline
from src.training.replay_buffer import ReplayBuffer
from src.training.self_play import SelfPlayGenerator, SelfPlaySample
from src.training.trainer import AlphaZeroTrainer, TrainerConfig


def build_stack():
    move_encoding = MoveEncoding()
    model = AlphaZeroNet(
        action_size=move_encoding.action_size,
        config=NetworkConfig(
            input_channels=20,
            board_size=8,
            num_filters=32,
            num_res_blocks=2,
            value_hidden_size=64,
        ),
    )
    inference = ModelInference(
        model=model,
        move_encoding=move_encoding,
        encoder=BoardEncoder(),
        device="cpu",
    )
    return move_encoding, model, inference


def make_dummy_sample(action_size: int) -> SelfPlaySample:
    state = np.zeros((20, 8, 8), dtype=np.float32)
    policy_target = np.zeros(action_size, dtype=np.float32)
    policy_target[0] = 1.0

    return SelfPlaySample(
        state=state,
        policy_target=policy_target,
        value_target=1.0,
        player_to_move=True,
    )


def test_replay_buffer_add_and_sample():
    move_encoding, _, _ = build_stack()
    buffer = ReplayBuffer(capacity=10)

    sample = make_dummy_sample(move_encoding.action_size)
    buffer.add_sample(sample)

    assert len(buffer) == 1

    batch = buffer.sample_batch(1)
    assert len(batch) == 1
    assert isinstance(batch[0], SelfPlaySample)


def test_dataset_shapes():
    move_encoding, _, _ = build_stack()
    sample = make_dummy_sample(move_encoding.action_size)
    dataset = AlphaZeroDataset([sample])

    state, policy_target, value_target = dataset[0]

    assert state.shape == (20, 8, 8)
    assert policy_target.shape == (move_encoding.action_size,)
    assert value_target.shape == (1,)


def test_alphazero_loss_runs():
    move_encoding, model, _ = build_stack()

    states = torch.randn(2, 20, 8, 8)
    policy_target = torch.zeros(2, move_encoding.action_size)
    policy_target[:, 0] = 1.0
    value_target = torch.tensor([[1.0], [-1.0]])

    policy_logits, value_pred = model(states)
    total_loss, breakdown = alphazero_loss(
        policy_logits=policy_logits,
        value_pred=value_pred,
        policy_target=policy_target,
        value_target=value_target,
    )

    assert total_loss.item() > 0
    assert breakdown.total_loss > 0


def test_trainer_runs_one_epoch():
    move_encoding, model, _ = build_stack()

    samples = [make_dummy_sample(move_encoding.action_size) for _ in range(8)]
    trainer = AlphaZeroTrainer(
        model=model,
        device="cpu",
        config=TrainerConfig(
            batch_size=4,
            learning_rate=1e-3,
            num_epochs=1,
        ),
    )

    stats = trainer.train_epoch(samples)

    assert stats.num_batches > 0
    assert stats.total_loss >= 0


def test_replay_buffer_save_and_load(tmp_path):
    move_encoding = MoveEncoding()
    sample = make_dummy_sample(move_encoding.action_size)
    original = ReplayBuffer(capacity=5)
    original.add_sample(sample)

    path = tmp_path / "buffer.pkl"
    original.save(path)

    restored = ReplayBuffer(capacity=5)
    restored.load(path)

    assert len(restored) == 1
    assert isinstance(restored.buffer[0], SelfPlaySample)
    np.testing.assert_array_equal(restored.buffer[0].state, sample.state)


def test_max_move_adjudication_does_not_invent_material_win():
    generator = SelfPlayGenerator(
        inference=None,
        move_encoding=MoveEncoding(),
        adjudicate_on_max_moves=True,
        adjudication_threshold=0.0,
    )
    materially_unbalanced = chess.Board("4k3/8/8/8/8/8/PP6/4K3 w - - 0 1")

    assert generator._adjudicate_result(materially_unbalanced) == "1/2-1/2"


def test_legacy_replay_buffer_adds_empty_en_passant_plane(tmp_path):
    sample = make_dummy_sample(MoveEncoding().action_size)
    sample.state = sample.state[:19]
    legacy_path = tmp_path / "legacy.pkl"
    with legacy_path.open("wb") as handle:
        pickle.dump([sample], handle)

    restored = ReplayBuffer(capacity=10)
    restored.load(legacy_path)

    assert restored.buffer[0].state.shape == (20, 8, 8)
    assert np.all(restored.buffer[0].state[19] == 0.0)


def test_legacy_checkpoint_migrates_first_convolution_to_20_planes(tmp_path):
    move_encoding = MoveEncoding()
    old_model = AlphaZeroNet(
        action_size=move_encoding.action_size,
        config=NetworkConfig(
            input_channels=19,
            board_size=8,
            num_filters=8,
            num_res_blocks=1,
            value_hidden_size=16,
        ),
    )
    with torch.no_grad():
        old_model.input_block[0].weight.fill_(0.125)

    checkpoint_path = tmp_path / "legacy_checkpoint.pt"
    torch.save(
        {
            "epoch": 3,
            "model_state_dict": old_model.state_dict(),
            "optimizer_state_dict": None,
            "extra": {},
        },
        checkpoint_path,
    )

    new_model = AlphaZeroNet(
        action_size=move_encoding.action_size,
        config=NetworkConfig(
            input_channels=20,
            board_size=8,
            num_filters=8,
            num_res_blocks=1,
            value_hidden_size=16,
        ),
    )
    load_checkpoint(checkpoint_path, new_model)

    migrated = new_model.input_block[0].weight.detach()
    torch.testing.assert_close(migrated[:, :19], old_model.input_block[0].weight)
    assert torch.count_nonzero(migrated[:, 19]).item() == 0


def test_self_play_game_report_contains_pgn_and_termination(tmp_path):
    logger = MetricsLogger(tmp_path)
    logger.append_self_play_game(
        iteration=2,
        game_number=3,
        result="1/2-1/2",
        moves=["e2e4", "e7e5"],
        samples=2,
        elapsed_seconds=1.25,
        ended_by_move_limit=True,
    )

    record = json.loads((tmp_path / "self_play_games.jsonl").read_text().strip())
    assert record["termination"] == "move-cap draw"
    assert record["move_count"] == 2
    assert "1. e4 e5" in record["pgn"]


def test_value_targets_use_full_game_outcome_for_both_colours():
    generator = SelfPlayGenerator(inference=None, move_encoding=MoveEncoding())

    assert generator._value_for_player(1.0, chess.WHITE) == 1.0
    assert generator._value_for_player(1.0, chess.BLACK) == -1.0
    assert generator._value_for_player(-1.0, chess.WHITE) == -1.0
    assert generator._value_for_player(-1.0, chess.BLACK) == 1.0
    assert generator._value_for_player(0.0, chess.WHITE) == 0.0
    assert generator._value_for_player(0.0, chess.BLACK) == 0.0


def test_automatic_device_resolution_returns_supported_torch_device():
    device = AlphaZeroPipeline._resolve_device("auto")

    assert isinstance(device, torch.device)
    assert device.type in {"cuda", "mps", "cpu"}


def test_replay_journal_recovers_games_and_avoids_duplicate_replay(tmp_path):
    sample = make_dummy_sample(MoveEncoding().action_size)
    snapshot = tmp_path / "latest_buffer.pkl"

    writer = ReplayBuffer(capacity=10)
    writer.save_game([sample], snapshot, iteration=1, game_number=1)

    recovered = ReplayBuffer(capacity=10)
    recovered.load(snapshot)
    assert len(recovered) == 1

    recovered.save(snapshot)
    restored_again = ReplayBuffer(capacity=10)
    restored_again.load(snapshot)

    assert len(restored_again) == 1
    assert not (tmp_path / "latest_buffer_journal").exists() or not list(
        (tmp_path / "latest_buffer_journal").glob("*.pkl")
    )


def test_self_play_emits_completed_game_callback_and_neutral_move_cap():
    move_encoding, _, inference = build_stack()
    generator = SelfPlayGenerator(
        inference=inference,
        move_encoding=move_encoding,
        mcts_config=MCTSConfig(num_simulations=2, add_dirichlet_noise=False),
        max_moves=4,
        opening_temperature_moves=10,
        opening_temperature=1.0,
        late_temperature=0.3,
        adjudicate_on_max_moves=True,
    )
    completed = []
    games = generator.generate_games(
        1,
        on_game_complete=lambda number, result, elapsed: completed.append(
            (number, result, elapsed)
        ),
    )

    assert len(games) == 1
    assert len(completed) == 1
    assert completed[0][0] == 1
    assert completed[0][2] >= 0.0
    assert games[0].ended_by_move_limit
    assert games[0].result == "1/2-1/2"
    assert all(sample.value_target == 0.0 for sample in games[0].samples)
