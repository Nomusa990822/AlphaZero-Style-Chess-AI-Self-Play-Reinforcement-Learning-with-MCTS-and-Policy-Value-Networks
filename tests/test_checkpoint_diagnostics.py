import chess
import numpy as np

from checkpoint_diagnostics import legal_policy_ranking
from src.engine.move_encoding import MoveEncoding


def test_legal_policy_ranking_masks_illegal_actions_and_normalizes():
    board = chess.Board()
    encoding = MoveEncoding()
    probabilities = np.zeros(encoding.action_size, dtype=np.float32)
    e4 = chess.Move.from_uci("e2e4")
    d4 = chess.Move.from_uci("d2d4")
    probabilities[encoding.move_to_tensor_index(e4, board)] = 0.6
    probabilities[encoding.move_to_tensor_index(d4, board)] = 0.3
    # A high-probability action that is not legal in this position must be ignored.
    probabilities[0] = 0.9

    ranking = legal_policy_ranking(board, probabilities, encoding)

    assert ranking[0]["move"] == "e2e4"
    assert ranking[0]["probability"] == 2 / 3
    assert ranking[1]["move"] == "d2d4"
    assert sum(item["probability"] for item in ranking) == pytest.approx(1.0)


def test_legal_policy_ranking_is_deterministic_on_ties():
    import pytest

    board = chess.Board()
    encoding = MoveEncoding()
    probabilities = np.zeros(encoding.action_size, dtype=np.float32)
    for uci in ("e2e4", "d2d4"):
        move = chess.Move.from_uci(uci)
        probabilities[encoding.move_to_tensor_index(move, board)] = 0.5

    ranking = legal_policy_ranking(board, probabilities, encoding)

    assert [item["move"] for item in ranking[:2]] == ["d2d4", "e2e4"]
