"""Regression tests for tactical safety at the MCTS root."""

import chess
import numpy as np

from src.engine.move_encoding import MoveEncoding
from src.mcts.node import MCTSNode
from src.mcts.search import MCTS, MCTSConfig
from src.mcts.tactics import find_mate_in_one, find_moves_avoiding_mate_in_one


FORCED_MATE_FEN = "k6r/8/8/4n3/2b4q/8/8/6K1 w - - 0 1"


def test_safety_filter_reports_when_every_legal_move_allows_mate():
    # This is a forced-loss position: every legal white move permits a
    # black checkmate on the following turn. The filter must report no
    # falsely "safe" escape and must leave the board unchanged.
    board = chess.Board(FORCED_MATE_FEN)
    original_fen = board.fen()
    legal_moves = list(board.legal_moves)

    safe_moves = find_moves_avoiding_mate_in_one(board)
    safe_uci = {move.uci() for move in safe_moves}

    unsafe_moves = []
    for move in legal_moves:
        if move.uci() in safe_uci:
            continue
        board.push(move)
        try:
            if find_mate_in_one(board):
                unsafe_moves.append(move)
        finally:
            board.pop()

    assert legal_moves
    assert not safe_moves
    assert len(unsafe_moves) == len(legal_moves)
    assert board.fen() == original_fen


def test_mcts_policy_falls_back_to_all_root_children_when_no_safe_move_exists():
    board = chess.Board(FORCED_MATE_FEN)
    encoding = MoveEncoding()
    root = MCTSNode(board=board)
    legal_uci = {move.uci() for move in board.legal_moves}
    root.expand({
        move_uci: 1.0 / len(legal_uci)
        for move_uci in legal_uci
    })

    search = MCTS(
        inference=None,
        move_encoding=encoding,
        config=MCTSConfig(num_simulations=1, add_dirichlet_noise=False),
    )

    full_probs, move_probs = search.get_action_probs(root, temperature=1.0)

    assert move_probs
    assert set(move_probs).issubset(legal_uci)
    assert np.isclose(float(full_probs.sum()), 1.0)
    assert all(prob > 0 for prob in move_probs.values())
