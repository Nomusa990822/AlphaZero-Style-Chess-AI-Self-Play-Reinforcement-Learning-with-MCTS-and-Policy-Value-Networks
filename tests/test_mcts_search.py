import chess
import numpy as np

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.dirichlet_noise import apply_dirichlet_noise
from src.mcts.node import MCTSNode
from src.mcts.puct import compute_puct_score, select_best_child
from src.mcts.search import MCTS, MCTSConfig
from src.mcts.tactics import find_mate_in_one
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig


def build_test_stack():
    move_encoding = MoveEncoding()
    model = AlphaZeroNet(
        action_size=move_encoding.action_size,
        config=NetworkConfig(
            input_channels=20,
            board_size=8,
            num_filters=64,
            num_res_blocks=2,
            value_hidden_size=128,
        ),
    )
    inference = ModelInference(
        model=model,
        move_encoding=move_encoding,
        encoder=BoardEncoder(),
        device="cpu",
    )
    return move_encoding, inference


def test_dirichlet_noise_preserves_distribution():
    priors = {"e2e4": 0.5, "d2d4": 0.3, "g1f3": 0.2}
    noisy = apply_dirichlet_noise(priors, alpha=0.3, epsilon=0.25, seed=42)

    assert set(noisy.keys()) == set(priors.keys())
    assert abs(sum(noisy.values()) - 1.0) < 1e-9
    assert noisy != priors


def test_puct_selects_some_child():
    board = chess.Board()
    root = MCTSNode(board=board)

    priors = {move.uci(): 1 / 20 for move in board.legal_moves}
    root.expand(priors)
    root.visit_count = 10

    child = select_best_child(root, c_puct=1.5)
    assert child is not None
    assert child.move in board.legal_moves


def test_compute_puct_score_returns_float():
    board = chess.Board()
    root = MCTSNode(board=board)

    priors = {move.uci(): 1 / 20 for move in board.legal_moves}
    root.expand(priors)
    root.visit_count = 10

    child = next(iter(root.children.values()))
    score = compute_puct_score(root, child, c_puct=1.5)

    assert isinstance(score, float)


def test_puct_negates_child_value_for_parent_perspective():
    board = chess.Board()
    parent = MCTSNode(board=board)
    parent.expand({"e2e4": 0.5, "d2d4": 0.5})
    parent.visit_count = 20

    good_for_parent = parent.children["e2e4"]
    bad_for_parent = parent.children["d2d4"]
    good_for_parent.visit_count = 4
    bad_for_parent.visit_count = 4
    # Child values are from the opponent-to-move perspective.
    good_for_parent.value_sum = -3.2  # opponent is losing: good for parent
    bad_for_parent.value_sum = 3.2    # opponent is winning: bad for parent

    good_score = compute_puct_score(parent, good_for_parent, c_puct=0.0)
    bad_score = compute_puct_score(parent, bad_for_parent, c_puct=0.0)

    assert good_score == 0.8
    assert bad_score == -0.8
    assert select_best_child(parent, c_puct=0.0) is good_for_parent


def test_mcts_run_expands_root():
    board = chess.Board()
    move_encoding, inference = build_test_stack()

    mcts = MCTS(
        inference=inference,
        move_encoding=move_encoding,
        config=MCTSConfig(
            num_simulations=25,
            c_puct=1.5,
            add_dirichlet_noise=False,
            temperature=1.0,
        ),
    )

    root = mcts.run(board)

    assert root.expanded()
    assert len(root.children) > 0
    assert root.visit_count > 0


def test_mcts_select_action_returns_legal_move():
    board = chess.Board()
    move_encoding, inference = build_test_stack()

    mcts = MCTS(
        inference=inference,
        move_encoding=move_encoding,
        config=MCTSConfig(
            num_simulations=20,
            add_dirichlet_noise=False,
            temperature=0.0,
        ),
    )

    root = mcts.run(board)
    move = mcts.select_action(root, temperature=0.0)

    assert move in board.legal_moves


def test_get_action_probs_matches_action_space():
    board = chess.Board()
    move_encoding, inference = build_test_stack()

    mcts = MCTS(
        inference=inference,
        move_encoding=move_encoding,
        config=MCTSConfig(
            num_simulations=15,
            add_dirichlet_noise=False,
            temperature=1.0,
        ),
    )

    root = mcts.run(board)
    full_probs, move_probs = mcts.get_action_probs(root, temperature=1.0)

    assert isinstance(full_probs, np.ndarray)
    assert full_probs.shape == (move_encoding.action_size,)
    assert abs(float(full_probs.sum()) - 1.0) < 1e-6
    assert abs(sum(move_probs.values()) - 1.0) < 1e-9

    for move_uci, prob in move_probs.items():
        idx = move_encoding.uci_to_index(move_uci, board)
        assert abs(float(full_probs[idx]) - prob) < 1e-6


def test_mcts_handles_terminal_position():
    board = chess.Board("7k/5Q2/7K/8/8/8/8/8 b - - 0 1")
    move_encoding, inference = build_test_stack()

    mcts = MCTS(
        inference=inference,
        move_encoding=move_encoding,
        config=MCTSConfig(num_simulations=5, add_dirichlet_noise=False),
    )

    root = mcts.run(board)

    assert root.is_terminal()
    assert len(root.children) == 0


def test_puct_uses_correct_perspective_when_black_moves():
    board = chess.Board()
    board.push_uci("e2e4")
    parent = MCTSNode(board=board)
    parent.expand({"e7e5": 0.5, "c7c5": 0.5})
    parent.visit_count = 20

    good_for_black = parent.children["e7e5"]
    bad_for_black = parent.children["c7c5"]
    good_for_black.visit_count = 4
    bad_for_black.visit_count = 4
    good_for_black.value_sum = -3.2
    bad_for_black.value_sum = 3.2

    assert compute_puct_score(parent, good_for_black, 0.0) == 0.8
    assert compute_puct_score(parent, bad_for_black, 0.0) == -0.8
    assert select_best_child(parent, 0.0) is good_for_black


def test_mcts_root_preserves_threefold_repetition_history():
    board = chess.Board()
    for move in ("g1f3", "g8f6", "f3g1", "f6g8",
                 "g1f3", "g8f6", "f3g1", "f6g8"):
        board.push_uci(move)

    move_encoding, inference = build_test_stack()
    mcts = MCTS(
        inference=inference,
        move_encoding=move_encoding,
        config=MCTSConfig(num_simulations=2, add_dirichlet_noise=False),
    )

    root = mcts.run(board)

    assert root.is_terminal()
    assert root.terminal_value() == 0.0


def test_exact_tactical_detector_finds_mate_in_one_for_white():
    board = chess.Board("7k/5Q2/5K2/8/8/8/8/8 w - - 0 1")

    mating_moves = find_mate_in_one(board)

    assert chess.Move.from_uci("f7g7") in mating_moves
    assert board.turn == chess.WHITE
    assert board.fen() == "7k/5Q2/5K2/8/8/8/8/8 w - - 0 1"


def test_exact_tactical_detector_finds_mate_in_one_for_black():
    board = chess.Board("8/8/8/8/8/5k2/5q2/7K b - - 0 1")

    mating_moves = find_mate_in_one(board)

    assert chess.Move.from_uci("f2g2") in mating_moves
    assert board.turn == chess.BLACK


def test_mcts_action_selection_prioritizes_forced_mate_and_policy_target():
    board = chess.Board("7k/5Q2/5K2/8/8/8/8/8 w - - 0 1")
    encoding = MoveEncoding()
    root = MCTSNode(board=board)
    root.expand({move.uci(): 1.0 / board.legal_moves.count() for move in board.legal_moves})

    search = MCTS(
        inference=None,
        move_encoding=encoding,
        config=MCTSConfig(num_simulations=1, add_dirichlet_noise=False),
    )

    selected = search.select_action(root, temperature=1.0)
    full_probs, move_probs = search.get_action_probs(root, temperature=1.0)

    assert selected.uci() == "f7g7"
    assert move_probs == {"f7g7": 1.0}
    assert np.isclose(float(full_probs.sum()), 1.0)
    assert np.count_nonzero(full_probs) == 1
