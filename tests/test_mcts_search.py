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


def test_one_ply_safety_filter_keeps_starting_position_moves_and_preserves_board():
    from src.mcts.tactics import find_moves_avoiding_mate_in_one

    board = chess.Board()
    original_fen = board.fen()

    safe_moves = find_moves_avoiding_mate_in_one(board)

    assert set(safe_moves) == set(board.legal_moves)
    assert board.fen() == original_fen



def test_puct_can_restrict_selection_to_supplied_candidates():
    board = chess.Board()
    root = MCTSNode(board=board)
    root.expand({"e2e4": 0.5, "d2d4": 0.5})
    root.visit_count = 10

    excluded = root.children["e2e4"]
    eligible = root.children["d2d4"]
    excluded.visit_count = 10
    eligible.visit_count = 0

    assert select_best_child(root, c_puct=0.0, candidates=[eligible]) is eligible


def test_mcts_spends_root_simulations_on_mate_in_one_only():
    board = chess.Board("7k/5Q2/5K2/8/8/8/8/8 w - - 0 1")
    encoding = MoveEncoding()

    class UniformInference:
        def predict(self, position):
            return np.ones(encoding.action_size, dtype=np.float32), 0.0

    search = MCTS(
        inference=UniformInference(),
        move_encoding=encoding,
        config=MCTSConfig(
            num_simulations=5,
            add_dirichlet_noise=False,
            temperature=1.0,
        ),
    )

    root = search.run(board)

    assert root.children["f7g7"].visit_count == 5
    assert all(
        child.visit_count == 0
        for move_uci, child in root.children.items()
        if move_uci != "f7g7"
    )
    assert search.select_action(root, temperature=0.0).uci() == "f7g7"



def test_mcts_spends_black_root_simulations_on_mate_in_one_only():
    board = chess.Board("8/8/8/8/8/5k2/5q2/7K b - - 0 1")
    encoding = MoveEncoding()

    class UniformInference:
        def predict(self, position):
            return np.ones(encoding.action_size, dtype=np.float32), 0.0

    search = MCTS(
        inference=UniformInference(),
        move_encoding=encoding,
        config=MCTSConfig(
            num_simulations=5,
            add_dirichlet_noise=False,
            temperature=1.0,
        ),
    )

    root = search.run(board)
    mating_uci = {move.uci() for move in find_mate_in_one(board)}

    assert mating_uci
    assert sum(root.children[move].visit_count for move in mating_uci) == 5
    assert all(
        child.visit_count == 0
        for move_uci, child in root.children.items()
        if move_uci not in mating_uci
    )


def test_mcts_forced_loss_fallback_keeps_all_root_moves_eligible():
    board = chess.Board("k6r/8/8/4n3/2b4q/8/8/6K1 w - - 0 1")
    encoding = MoveEncoding()

    class UniformInference:
        def predict(self, position):
            return np.ones(encoding.action_size, dtype=np.float32), 0.0

    search = MCTS(
        inference=UniformInference(),
        move_encoding=encoding,
        config=MCTSConfig(
            num_simulations=5,
            add_dirichlet_noise=False,
            temperature=1.0,
        ),
    )

    root = search.run(board)
    eligible = search._root_children_for_action(root)

    assert eligible
    assert {child.move.uci() for child in eligible} == {
        move.uci() for move in board.legal_moves
    }
    assert sum(child.visit_count for child in root.children.values()) == 5
    assert search.select_action(root, temperature=0.0) in board.legal_moves



def test_disabling_tactical_root_filter_allows_normal_visit_based_selection():
    board = chess.Board("7k/5Q2/5K2/8/8/8/8/8 w - - 0 1")
    encoding = MoveEncoding()
    root = MCTSNode(board=board)
    root.expand({move.uci(): 1.0 / board.legal_moves.count() for move in board.legal_moves})
    mating = {move.uci() for move in find_mate_in_one(board)}
    non_mating = next(
        child for move_uci, child in root.children.items()
        if move_uci not in mating
    )
    non_mating.visit_count = 20

    search = MCTS(
        inference=None,
        move_encoding=encoding,
        config=MCTSConfig(
            num_simulations=1,
            add_dirichlet_noise=False,
            use_tactical_root_filter=False,
        ),
    )

    selected = search.select_action(root, temperature=0.0)
    full_probs, move_probs = search.get_action_probs(root, temperature=0.0)

    assert selected == non_mating.move
    assert set(move_probs) == set(root.children)
    assert np.isclose(float(full_probs.sum()), 1.0)
    assert move_probs[selected.uci()] == 1.0



def test_root_tactical_analysis_is_reused_for_action_and_policy(monkeypatch):
    import src.mcts.search as search_module

    calls = {"mate_in_one": 0, "mate_in_two": 0, "mate_avoidance": 0}

    def no_mate(position):
        calls["mate_in_one"] += 1
        return []

    def no_forced_mate(position):
        calls["mate_in_two"] += 1
        return []

    def all_moves_safe(position):
        calls["mate_avoidance"] += 1
        return list(position.legal_moves)

    monkeypatch.setattr(search_module, "find_mate_in_one", no_mate)
    monkeypatch.setattr(search_module, "find_forced_mate_in_two", no_forced_mate)
    monkeypatch.setattr(
        search_module, "find_moves_avoiding_mate_in_one", all_moves_safe
    )

    board = chess.Board()
    encoding = MoveEncoding()
    root = MCTSNode(board=board)
    root.expand({
        move.uci(): 1.0 / board.legal_moves.count()
        for move in board.legal_moves
    })
    search = MCTS(
        inference=None,
        move_encoding=encoding,
        config=MCTSConfig(num_simulations=1, add_dirichlet_noise=False),
    )

    first_candidates = search._root_children_for_action(root)
    selected = search.select_action(root, temperature=0.0)
    full_probs, move_probs = search.get_action_probs(root, temperature=1.0)

    assert len(first_candidates) == board.legal_moves.count()
    assert selected in board.legal_moves
    assert np.isclose(float(full_probs.sum()), 1.0)
    assert np.isclose(sum(move_probs.values()), 1.0)
    assert calls == {
        "mate_in_one": 1,
        "mate_in_two": 1,
        "mate_avoidance": 1,
    }



def test_root_see_prior_bias_rewards_captures_for_white_and_black(monkeypatch):
    import src.mcts.search as search_module

    positions = [
        (chess.Board("4k3/8/8/3p4/4P3/8/8/4K3 w - - 0 1"), "e4d5"),
        (chess.Board("4k3/8/8/4p3/3P4/8/8/4K3 b - - 0 1"), "e5d4"),
    ]

    for board, capture_uci in positions:
        original_fen = board.fen()

        def favourable_exchange(position, move, max_capture_nodes=128):
            return 300 if move.uci() == capture_uci else 0

        monkeypatch.setattr(
            search_module, "static_exchange_evaluation", favourable_exchange
        )
        encoding = MoveEncoding()

        class UniformInference:
            def predict(self, position):
                return np.ones(encoding.action_size, dtype=np.float32), 0.0

        root = MCTSNode(board=board)
        search = MCTS(
            inference=UniformInference(),
            move_encoding=encoding,
            config=MCTSConfig(
                num_simulations=0,
                add_dirichlet_noise=False,
                use_tactical_root_filter=False,
            ),
        )
        search._evaluate_and_expand(root, is_root=True)

        capture_prior = root.children[capture_uci].prior
        quiet_child = next(
            child for move_uci, child in root.children.items()
            if move_uci != capture_uci and not board.is_capture(child.move)
        )
        assert capture_prior > quiet_child.prior
        assert len(root.children) == board.legal_moves.count()
        assert np.isclose(sum(child.prior for child in root.children.values()), 1.0)
        assert board.fen() == original_fen


def test_root_see_prior_bias_deprioritizes_poisoned_capture_without_pruning(monkeypatch):
    import src.mcts.search as search_module

    board = chess.Board("4k3/8/8/3p4/4P3/8/8/4K3 w - - 0 1")
    capture_uci = "e4d5"

    def poisoned_exchange(position, move, max_capture_nodes=128):
        return -300 if move.uci() == capture_uci else 0

    monkeypatch.setattr(
        search_module, "static_exchange_evaluation", poisoned_exchange
    )
    encoding = MoveEncoding()

    class UniformInference:
        def predict(self, position):
            return np.ones(encoding.action_size, dtype=np.float32), 0.0

    root = MCTSNode(board=board)
    search = MCTS(
        inference=UniformInference(),
        move_encoding=encoding,
        config=MCTSConfig(
            num_simulations=0,
            add_dirichlet_noise=False,
            use_tactical_root_filter=False,
        ),
    )
    search._evaluate_and_expand(root, is_root=True)

    capture_prior = root.children[capture_uci].prior
    quiet_child = next(
        child for move_uci, child in root.children.items()
        if move_uci != capture_uci and not board.is_capture(child.move)
    )
    assert capture_prior < quiet_child.prior
    assert set(root.children) == {move.uci() for move in board.legal_moves}
    assert np.isclose(sum(child.prior for child in root.children.values()), 1.0)


def test_root_see_budget_exhaustion_preserves_neural_capture_prior(monkeypatch):
    import src.mcts.search as search_module

    board = chess.Board("4k3/8/8/3p4/4P3/8/8/4K3 w - - 0 1")
    capture_uci = "e4d5"

    monkeypatch.setattr(
        search_module,
        "static_exchange_evaluation",
        lambda position, move, max_capture_nodes=128: None,
    )
    encoding = MoveEncoding()

    class UniformInference:
        def predict(self, position):
            return np.ones(encoding.action_size, dtype=np.float32), 0.0

    root = MCTSNode(board=board)
    search = MCTS(
        inference=UniformInference(),
        move_encoding=encoding,
        config=MCTSConfig(
            num_simulations=0,
            add_dirichlet_noise=False,
            use_tactical_root_filter=False,
        ),
    )
    search._evaluate_and_expand(root, is_root=True)

    assert np.isclose(
        root.children[capture_uci].prior,
        next(
            child.prior for move_uci, child in root.children.items()
            if move_uci != capture_uci and not board.is_capture(child.move)
        ),
    )


def test_root_see_bias_fast_path_skips_copy_and_scoring_without_tactics(monkeypatch):
    import src.mcts.search as search_module

    board = chess.Board()
    priors = {
        move.uci(): 1.0 / board.legal_moves.count()
        for move in board.legal_moves
    }
    encoding = MoveEncoding()
    search = MCTS(
        inference=None,
        move_encoding=encoding,
        config=MCTSConfig(
            num_simulations=0,
            add_dirichlet_noise=False,
            use_tactical_root_filter=False,
        ),
    )

    def unexpected_see_call(*args, **kwargs):
        raise AssertionError("SEE must not run when no captures/promotions exist")

    monkeypatch.setattr(
        search_module, "static_exchange_evaluation", unexpected_see_call
    )

    result = search._apply_static_exchange_prior_bias(board, priors)

    assert result is priors
    assert len(result) == board.legal_moves.count()
    assert np.isclose(sum(result.values()), 1.0)



def test_root_tactical_cache_invalidates_when_filter_configuration_changes(monkeypatch):
    import src.mcts.search as search_module

    board = chess.Board("7k/5Q2/5K2/8/8/8/8/8 w - - 0 1")
    encoding = MoveEncoding()
    root = MCTSNode(board=board)
    root.expand({
        move.uci(): 1.0 / board.legal_moves.count()
        for move in board.legal_moves
    })
    mate_move = chess.Move.from_uci("f7g7")
    detector_calls = {"mate_in_one": 0}

    def one_known_mate(position):
        detector_calls["mate_in_one"] += 1
        return [mate_move]

    monkeypatch.setattr(search_module, "find_mate_in_one", one_known_mate)

    search = MCTS(
        inference=None,
        move_encoding=encoding,
        config=MCTSConfig(
            num_simulations=0,
            add_dirichlet_noise=False,
            use_tactical_root_filter=True,
        ),
    )

    filtered = search._root_children_for_action(root)
    assert [child.move for child in filtered] == [mate_move]
    assert search._cached_root_mating_moves == [mate_move]
    assert detector_calls["mate_in_one"] == 1

    # Disabling the filter must invalidate the cached tactical-only result.
    search.config.use_tactical_root_filter = False
    unfiltered = search._root_children_for_action(root)
    assert len(unfiltered) == board.legal_moves.count()
    assert search._cached_root_mating_moves == []
    assert detector_calls["mate_in_one"] == 1

    # Re-enabling it must recompute the tactical result for the same root.
    search.config.use_tactical_root_filter = True
    filtered_again = search._root_children_for_action(root)
    assert [child.move for child in filtered_again] == [mate_move]
    assert search._cached_root_mating_moves == [mate_move]
    assert detector_calls["mate_in_one"] == 2



def test_mate_in_one_action_and_policy_target_share_temperature_distribution(monkeypatch):
    import src.mcts.search as search_module

    board = chess.Board("7k/5Q2/5K2/8/8/8/8/8 w - - 0 1")
    encoding = MoveEncoding()
    root = MCTSNode(board=board)
    root.expand({
        move.uci(): 1.0 / board.legal_moves.count()
        for move in board.legal_moves
    })
    mating_moves = [
        chess.Move.from_uci("f7g7"),
        next(move for move in board.legal_moves if move.uci() != "f7g7"),
    ]
    monkeypatch.setattr(
        search_module, "find_mate_in_one", lambda position: mating_moves
    )
    monkeypatch.setattr(search_module.np.random, "choice", lambda size: size - 1)

    search = MCTS(
        inference=None,
        move_encoding=encoding,
        config=MCTSConfig(
            num_simulations=0,
            add_dirichlet_noise=False,
            temperature=1.0,
        ),
    )

    sampled_move = search.select_action(root, temperature=1.0)
    full_probs, move_probs = search.get_action_probs(root, temperature=1.0)

    assert sampled_move == mating_moves[1]
    assert move_probs == {
        mating_moves[0].uci(): 0.5,
        mating_moves[1].uci(): 0.5,
    }
    assert np.isclose(float(full_probs.sum()), 1.0)

    deterministic_move = search.select_action(root, temperature=0.0)
    deterministic_full_probs, deterministic_move_probs = search.get_action_probs(
        root, temperature=0.0
    )

    assert deterministic_move == mating_moves[0]
    assert deterministic_move_probs == {mating_moves[0].uci(): 1.0}
    assert np.isclose(float(deterministic_full_probs.sum()), 1.0)
    assert deterministic_full_probs[
        encoding.uci_to_index(mating_moves[0].uci(), board)
    ] == 1.0
    assert np.count_nonzero(deterministic_full_probs) == 1
