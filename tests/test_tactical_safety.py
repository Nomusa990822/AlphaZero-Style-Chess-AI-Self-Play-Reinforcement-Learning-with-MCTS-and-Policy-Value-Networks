"""Regression tests for tactical safety at the MCTS root."""

import chess
import numpy as np

from src.engine.move_encoding import MoveEncoding
from src.mcts.node import MCTSNode
from src.mcts.search import MCTS, MCTSConfig
from src.mcts.tactics import find_mate_in_one, find_moves_avoiding_mate_in_one


def test_one_ply_safety_filter_identifies_moves_that_allow_forced_mate():
    # White's king is under a mating net. The black queen, rook, bishop and
    # knight coordinate to make Qh2# possible after some careless replies.
    board = chess.Board("k6r/8/8/4n3/2b4q/8/8/6K1 w - - 0 1")
    original_fen = board.fen()

    safe_moves = find_moves_avoiding_mate_in_one(board)
    safe_uci = {move.uci() for move in safe_moves}

    unsafe_moves = []
    for move in list(board.legal_moves):
        if move.uci() in safe_uci:
            continue
        board.push(move)
        try:
            if find_mate_in_one(board):
                unsafe_moves.append(move)
        finally:
            board.pop()

    assert safe_moves
    assert unsafe_moves
    assert board.fen() == original_fen


def test_mcts_policy_excludes_moves_that_allow_immediate_mate():
    board = chess.Board("k6r/8/8/4n3/2b4q/8/8/6K1 w - - 0 1")
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
    safe_uci = {
        move.uci()
        for move in find_moves_avoiding_mate_in_one(board)
    }

    full_probs, move_probs = search.get_action_probs(root, temperature=1.0)

    assert move_probs
    assert set(move_probs).issubset(safe_uci)
    assert np.isclose(float(full_probs.sum()), 1.0)
    assert all(prob > 0 for prob in move_probs.values())
