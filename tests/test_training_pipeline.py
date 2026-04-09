import numpy as np
import torch

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.dataset import AlphaZeroDataset
from src.training.loss import alphazero_loss
from src.training.replay_buffer import ReplayBuffer
from src.training.self_play import SelfPlaySample
from src.training.trainer import AlphaZeroTrainer, TrainerConfig


def build_stack():
    move_encoding = MoveEncoding()
    model = AlphaZeroNet(
        action_size=move_encoding.action_size,
        config=NetworkConfig(
            input_channels=19,
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
    state = np.zeros((19, 8, 8), dtype=np.float32)
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

    assert state.shape == (19, 8, 8)
    assert policy_target.shape == (move_encoding.action_size,)
    assert value_target.shape == (1,)


def test_alphazero_loss_runs():
    move_encoding, model, _ = build_stack()

    states = torch.randn(2, 19, 8, 8)
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
