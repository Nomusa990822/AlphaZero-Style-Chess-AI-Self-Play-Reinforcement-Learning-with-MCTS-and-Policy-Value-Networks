"""Regression tests for tactical safety at the MCTS root."""

import chess
import numpy as np

from src.engine.move_encoding import MoveEncoding
from src.mcts.node import MCTSNode
from src.mcts.search import MCTS, MCTSConfig
from src.mcts.tactics import (
    find_mate_in_one,
    find_moves_avoiding_mate_in_one,
    static_exchange_evaluation,
)


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



def test_forced_mate_in_two_requires_every_opponent_reply(monkeypatch):
    import src.mcts.tactics as tactics

    board = chess.Board()
    original_fen = board.fen()
    original_stack = list(board.move_stack)

    def mocked_mate_in_one(position):
        if (
            len(position.move_stack) >= 2
            and position.move_stack[0] == chess.Move.from_uci("e2e4")
            and position.turn == chess.WHITE
        ):
            return [next(iter(position.legal_moves))]
        return []

    monkeypatch.setattr(tactics, "find_mate_in_one", mocked_mate_in_one)
    forced = tactics.find_forced_mate_in_two(board)

    assert forced == [chess.Move.from_uci("e2e4")]
    assert board.fen() == original_fen
    assert board.move_stack == original_stack


def test_forced_mate_in_two_discards_incomplete_candidate(monkeypatch):
    import src.mcts.tactics as tactics

    board = chess.Board()
    monkeypatch.setattr(
        tactics,
        "find_mate_in_one",
        lambda position: [next(iter(position.legal_moves))],
    )
    assert tactics.find_forced_mate_in_two(board, max_reply_checks=1) == []



def test_static_exchange_values_undefended_queen_capture_and_restores_board():
    board = chess.Board("4k3/8/8/3q4/8/8/3R4/4K3 w - - 0 1")
    move = chess.Move.from_uci("d2d5")
    original_fen = board.fen()
    original_stack = list(board.move_stack)

    assert static_exchange_evaluation(board, move) == 900
    assert board.fen() == original_fen
    assert board.move_stack == original_stack


def test_static_exchange_rejects_poisoned_rook_capture():
    board = chess.Board("3qk3/8/8/3p4/8/8/3R4/4K3 w - - 0 1")
    move = chess.Move.from_uci("d2d5")

    # White wins a pawn but loses the rook to the black queen.
    assert static_exchange_evaluation(board, move) == -400


def test_static_exchange_handles_en_passant_and_promotion_gain():
    en_passant = chess.Board("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
    assert static_exchange_evaluation(
        en_passant, chess.Move.from_uci("e5d6")
    ) == 100

    promotion = chess.Board("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
    assert static_exchange_evaluation(
        promotion, chess.Move.from_uci("a7a8q")
    ) == 800


def test_static_exchange_rejects_illegal_moves_and_invalid_budget():
    board = chess.Board()
    with np.testing.assert_raises(ValueError):
        static_exchange_evaluation(board, chess.Move.from_uci("e2e5"))
    with np.testing.assert_raises(ValueError):
        static_exchange_evaluation(
            board, chess.Move.from_uci("e2e4"), max_capture_nodes=0
        )
