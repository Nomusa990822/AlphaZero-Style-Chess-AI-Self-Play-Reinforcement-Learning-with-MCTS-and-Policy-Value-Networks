import chess
import torch

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.model.policy_head import PolicyHead
from src.model.residual_block import ResidualBlock
from src.model.value_head import ValueHead


def test_residual_block_shape():
    block = ResidualBlock(channels=64)
    x = torch.randn(4, 64, 8, 8)

    y = block(x)

    assert y.shape == (4, 64, 8, 8)


def test_policy_head_output_shape():
    head = PolicyHead(
        in_channels=128,
        board_size=8,
        action_size=5000,
        head_channels=2
    )
    x = torch.randn(3, 128, 8, 8)

    logits = head(x)

    assert logits.shape == (3, 5000)


def test_value_head_output_shape_and_range():
    head = ValueHead(
        in_channels=128,
        board_size=8,
        hidden_size=256,
        head_channels=1
    )
    x = torch.randn(5, 128, 8, 8)

    value = head(x)

    assert value.shape == (5, 1)
    assert torch.all(value <= 1.0)
    assert torch.all(value >= -1.0)


def test_alphazero_network_output_shapes():
    move_encoding = MoveEncoding()
    config = NetworkConfig(
        input_channels=19,
        board_size=8,
        num_filters=64,
        num_res_blocks=3,
        value_hidden_size=128
    )
    model = AlphaZeroNet(
        action_size=move_encoding.action_size,
        config=config
    )

    x = torch.randn(2, 19, 8, 8)
    policy_logits, value = model(x)

    assert policy_logits.shape == (2, move_encoding.action_size)
    assert value.shape == (2, 1)


def test_predict_outputs_probabilities():
    move_encoding = MoveEncoding()
    model = AlphaZeroNet(action_size=move_encoding.action_size)

    x = torch.randn(1, 19, 8, 8)
    policy_probs, value = model.predict(x)

    assert policy_probs.shape == (1, move_encoding.action_size)
    assert value.shape == (1, 1)

    probs_sum = policy_probs.sum(dim=1)
    assert torch.allclose(probs_sum, torch.ones_like(probs_sum), atol=1e-5)


def test_inference_on_initial_board():
    board = chess.Board()
    move_encoding = MoveEncoding()
    encoder = BoardEncoder()

    model = AlphaZeroNet(action_size=move_encoding.action_size)
    inference = ModelInference(
        model=model,
        move_encoding=move_encoding,
        encoder=encoder,
        device="cpu"
    )

    policy_probs, value = inference.predict(board)

    assert policy_probs.shape == (move_encoding.action_size,)
    assert isinstance(value, float)
    assert -1.0 <= value <= 1.0


def test_best_legal_move_returns_legal_move():
    board = chess.Board()
    move_encoding = MoveEncoding()
    encoder = BoardEncoder()

    model = AlphaZeroNet(action_size=move_encoding.action_size)
    inference = ModelInference(
        model=model,
        move_encoding=move_encoding,
        encoder=encoder,
        device="cpu"
    )

    move = inference.best_legal_move(board)

    assert move is not None
    assert move in board.legal_moves
