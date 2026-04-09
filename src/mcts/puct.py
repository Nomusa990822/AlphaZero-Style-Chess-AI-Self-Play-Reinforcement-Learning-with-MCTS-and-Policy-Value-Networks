"""
PUCT scoring for AlphaZero-style MCTS.
"""

from __future__ import annotations

import math

from src.mcts.node import MCTSNode


def compute_puct_score(parent: MCTSNode, child: MCTSNode, c_puct: float) -> float:
    """
    Compute the PUCT score for a child node.

    Formula:
        score = Q + U

    where:
        Q = child.q_value
        U = c_puct * prior * sqrt(parent_visits) / (1 + child_visits)

    Args:
        parent: Parent node
        child: Candidate child node
        c_puct: Exploration constant

    Returns:
        PUCT score
    """
    parent_visits = max(1, parent.visit_count)
    q_value = child.q_value
    u_value = (
        c_puct
        * child.prior
        * math.sqrt(parent_visits)
        / (1 + child.visit_count)
    )
    return q_value + u_value


def select_best_child(node: MCTSNode, c_puct: float) -> MCTSNode:
    """
    Select the child with highest PUCT score.

    Args:
        node: Expanded MCTS node
        c_puct: Exploration constant

    Returns:
        Best child node

    Raises:
        ValueError: If node has no children
    """
    if not node.children:
        raise ValueError("Cannot select child from node with no children.")

    best_child = max(
        node.children.values(),
        key=lambda child: compute_puct_score(node, child, c_puct)
    )
    return best_child
