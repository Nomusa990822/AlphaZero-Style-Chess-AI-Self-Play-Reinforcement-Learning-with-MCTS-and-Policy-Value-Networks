"""
PUCT scoring for AlphaZero-style MCTS.

Node values are always stored from the perspective of the player to move
at that node. A child therefore evaluates the position from the opponent's
perspective relative to its parent, so its Q value must be negated when the
parent selects among its actions.
"""

from __future__ import annotations

import math
from collections.abc import Iterable

from src.mcts.node import MCTSNode


def compute_puct_score(parent: MCTSNode, child: MCTSNode, c_puct: float) -> float:
    """Return the parent-player PUCT score for one child action."""
    parent_visits = max(1, parent.visit_count)
    # Child Q is from the child's side-to-move perspective (the opponent).
    # Convert it to the parent player's perspective before action selection.
    q_value = -child.q_value
    u_value = (
        c_puct
        * child.prior
        * math.sqrt(parent_visits)
        / (1 + child.visit_count)
    )
    return q_value + u_value


def select_best_child(
    node: MCTSNode,
    c_puct: float,
    candidates: Iterable[MCTSNode] | None = None,
) -> MCTSNode:
    """Select the highest-scoring child, optionally from a restricted set.

    candidates lets the root search apply exact tactical safety constraints
    without deleting legal children from the tree. Non-root selection remains
    unrestricted unless a caller explicitly supplies candidates.
    """
    eligible = list(node.children.values()) if candidates is None else list(candidates)
    if not eligible:
        raise ValueError("Cannot select child from an empty candidate set.")

    return max(
        eligible,
        key=lambda child: compute_puct_score(node, child, c_puct),
    )
