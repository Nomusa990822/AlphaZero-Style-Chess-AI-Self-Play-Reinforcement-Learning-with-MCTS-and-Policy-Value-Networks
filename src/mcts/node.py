"""
Tree node definition for AlphaZero-style Monte Carlo Tree Search.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

import chess


@dataclass
class MCTSNode:
    """
    A single node in the MCTS tree.

    Attributes:
        board: Current chess position.
        parent: Parent node.
        prior: Prior probability from policy network.
        move: The move that led from parent -> this node.
        children: Mapping from move UCI to child node.
        visit_count: Number of times node was visited.
        value_sum: Sum of backed-up values from node perspective.
        is_expanded: Whether this node has been expanded yet.
    """
    board: chess.Board
    parent: Optional["MCTSNode"] = None
    prior: float = 0.0
    move: Optional[chess.Move] = None
    children: Dict[str, "MCTSNode"] = field(default_factory=dict)
    visit_count: int = 0
    value_sum: float = 0.0
    is_expanded: bool = False

    def expanded(self) -> bool:
        """
        Return whether the node has been expanded.
        """
        return self.is_expanded

    @property
    def q_value(self) -> float:
        """
        Mean value of this node from this node's perspective.

        Returns:
            Average backed-up value. Returns 0 if unvisited.
        """
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count

    def expand(self, policy_probs: dict[str, float]) -> None:
        """
        Expand the node by creating children for all legal moves.

        Args:
            policy_probs: Mapping from move UCI -> probability prior
        """
        if self.is_expanded:
            return

        legal_moves = list(self.board.legal_moves)
        for move in legal_moves:
            move_uci = move.uci()
            prior = float(policy_probs.get(move_uci, 0.0))

            child_board = self.board.copy(stack=False)
            child_board.push(move)

            self.children[move_uci] = MCTSNode(
                board=child_board,
                parent=self,
                prior=prior,
                move=move,
            )

        self.is_expanded = True

    def is_terminal(self) -> bool:
        """
        Check whether the node position is terminal.
        """
        return self.board.is_game_over()

    def terminal_value(self) -> float:
        """
        Return terminal result from side-to-move perspective.

        Convention:
            +1 : side to move eventually wins
            -1 : side to move eventually loses
             0 : draw

        Returns:
            Scalar value in [-1, 1]
        """
        outcome = self.board.outcome()
        if outcome is None or outcome.winner is None:
            return 0.0

        # outcome.winner is True for white, False for black
        side_to_move = self.board.turn
        return 1.0 if outcome.winner == side_to_move else -1.0

    def add_noise_to_priors(self, noisy_priors: dict[str, float]) -> None:
        """
        Replace child priors with noisy values.

        Args:
            noisy_priors: Mapping from move UCI -> noisy prior
        """
        for move_uci, child in self.children.items():
            if move_uci in noisy_priors:
                child.prior = float(noisy_priors[move_uci])

    def select_child_by_visit_count(self) -> Optional["MCTSNode"]:
        """
        Return child with highest visit count.

        Returns:
            Best child or None if no children exist.
        """
        if not self.children:
            return None
        return max(self.children.values(), key=lambda child: child.visit_count)

    def get_visit_distribution(self) -> dict[str, float]:
        """
        Convert child visit counts into a normalized distribution.

        Returns:
            Mapping from move UCI -> visit probability
        """
        total_visits = sum(child.visit_count for child in self.children.values())
        if total_visits == 0:
            if not self.children:
                return {}
            uniform = 1.0 / len(self.children)
            return {move_uci: uniform for move_uci in self.children}

        return {
            move_uci: child.visit_count / total_visits
            for move_uci, child in self.children.items()
        }
