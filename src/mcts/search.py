"""
AlphaZero-style Monte Carlo Tree Search.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import chess
import numpy as np

from src.engine.move_encoding import MoveEncoding
from src.mcts.dirichlet_noise import apply_dirichlet_noise
from src.mcts.node import MCTSNode
from src.mcts.puct import select_best_child
from src.mcts.tactics import (\n    find_forced_mate_in_two,\n    find_mate_in_one,\n    find_moves_avoiding_mate_in_one,\n)
from src.model.inference import ModelInference


@dataclass
class MCTSConfig:
    """
    Configuration for MCTS.
    """
    num_simulations: int = 100
    c_puct: float = 1.5
    dirichlet_alpha: float = 0.3
    dirichlet_epsilon: float = 0.25
    add_dirichlet_noise: bool = True
    temperature: float = 1.0
    use_tactical_root_filter: bool = True


class MCTS:
    """
    AlphaZero-style MCTS using a policy-value network.
    """

    def __init__(
        self,
        inference: ModelInference,
        move_encoding: MoveEncoding,
        config: MCTSConfig | None = None,
    ) -> None:
        """
        Args:
            inference: Neural inference helper
            move_encoding: Move encoder
            config: MCTS configuration
        """
        self.inference = inference
        self.move_encoding = move_encoding
        self.config = config or MCTSConfig()

    def _policy_dict_for_board(
        self,
        board: chess.Board,
        policy_probs: np.ndarray,
    ) -> dict[str, float]:
        """
        Convert full action policy vector into legal move priors only.

        Args:
            board: Current board
            policy_probs: Full action distribution

        Returns:
            Mapping legal move UCI -> normalized probability
        """
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return {}

        priors = {}
        for move in legal_moves:
            idx = self.move_encoding.move_to_tensor_index(move, board)
            priors[move.uci()] = float(policy_probs[idx])

        total = sum(priors.values())
        if total <= 0:
            uniform = 1.0 / len(priors)
            return {move_uci: uniform for move_uci in priors}

        return {move_uci: prob / total for move_uci, prob in priors.items()}

    def _evaluate_and_expand(self, node: MCTSNode, is_root: bool = False) -> float:
        """
        Evaluate a leaf node and expand it.

        Args:
            node: Node to evaluate
            is_root: Whether this is the root node

        Returns:
            Value from node's perspective
        """
        if node.is_terminal():
            return node.terminal_value()

        policy_probs, value = self.inference.predict(node.board)
        priors = self._policy_dict_for_board(node.board, policy_probs)

        node.expand(priors)

        if is_root and self.config.add_dirichlet_noise and node.children:
            noisy_priors = apply_dirichlet_noise(
                priors,
                alpha=self.config.dirichlet_alpha,
                epsilon=self.config.dirichlet_epsilon,
            )
            node.add_noise_to_priors(noisy_priors)

        return float(value)

    def _backpropagate(self, search_path: list[MCTSNode], leaf_value: float) -> None:
        """
        Backpropagate evaluation value up the search path.

        Important:
        Each parent node is from the opposite player's perspective,
        so the value sign flips each step upward.

        Args:
            search_path: Nodes from root to leaf
            leaf_value: Value from leaf node perspective
        """
        value = leaf_value
        for node in reversed(search_path):
            node.visit_count += 1
            node.value_sum += value
            value = -value

    def run(self, board: chess.Board) -> MCTSNode:
        """
        Run MCTS from a board position and return the root node.

        Args:
            board: Starting position

        Returns:
            Root node after simulations
        """
        root = MCTSNode(board=board.copy(stack=True))
        root_value = self._evaluate_and_expand(root, is_root=True)
        root.visit_count += 1
        root.value_sum += root_value

        # Apply exact one-ply safety (and mate-in-one priority) once at the
        # root. Reusing this candidate set prevents simulations being spent
        # on root moves that the final action/policy would later discard.
        root_search_children = (
            self._root_children_for_action(root)
            if self.config.use_tactical_root_filter
            else list(root.children.values())
        )

        for _ in range(self.config.num_simulations):
            node = root
            search_path = [node]

            # Selection
            while node.expanded() and node.children:
                if node is root:
                    node = select_best_child(
                        node,
                        self.config.c_puct,
                        candidates=root_search_children,
                    )
                else:
                    node = select_best_child(node, self.config.c_puct)
                search_path.append(node)

            # Expansion / evaluation
            leaf_value = self._evaluate_and_expand(node, is_root=False)

            # Backup
            self._backpropagate(search_path, leaf_value)

        return root

    def _root_children_for_action(self, root: MCTSNode) -> list[MCTSNode]:
        """
        Apply a one-ply checkmate-safety filter to root actions.

        If at least one move avoids immediate mate, unsafe moves are excluded.
        If every move permits mate, retain all children so MCTS can still rank
        the least-bad continuation.
        """
        children = list(root.children.values())
        if not self.config.use_tactical_root_filter:
            return children
        mating_moves = find_mate_in_one(root.board.copy(stack=True))
        if mating_moves:
            mating_uci = {move.uci() for move in mating_moves}
            mating_children = [
                child for child in children if child.move.uci() in mating_uci
            ]
            return mating_children or children

        forced_mates = find_forced_mate_in_two(root.board.copy(stack=True))\n        if forced_mates:\n            forced_uci = {move.uci() for move in forced_mates}\n            forced_children = [child for child in children if child.move.uci() in forced_uci]\n            if forced_children:\n                return forced_children\n\n        safe_moves = find_moves_avoiding_mate_in_one(root.board.copy(stack=True))
        if not safe_moves:
            return children

        safe_uci = {move.uci() for move in safe_moves}
        filtered = [child for child in children if child.move.uci() in safe_uci]
        return filtered or children

    def select_action(self, root: MCTSNode, temperature: float | None = None) -> chess.Move:
        """
        Select move from root visit counts.

        Args:
            root: Root node after search
            temperature: Optional override

        Returns:
            Selected chess move

        Raises:
            ValueError: If root has no children
        """
        if not root.children:
            raise ValueError("Root has no children; cannot select action.")

        if self.config.use_tactical_root_filter:
            mating_moves = find_mate_in_one(root.board.copy(stack=True))
            if mating_moves:
                return mating_moves[0]

        children = self._root_children_for_action(root)
        temperature = self.config.temperature if temperature is None else temperature
        visits = np.array([child.visit_count for child in children], dtype=np.float64)

        if temperature <= 1e-8:
            best_idx = int(np.argmax(visits))
            return children[best_idx].move

        adjusted = visits ** (1.0 / temperature)
        total = adjusted.sum()
        if total <= 0:
            probs = np.full_like(adjusted, 1.0 / len(adjusted))
        else:
            probs = adjusted / total

        selected_idx = int(np.random.choice(len(children), p=probs))
        return children[selected_idx].move

    def get_action_probs(
        self,
        root: MCTSNode,
        temperature: float | None = None,
    ) -> Tuple[np.ndarray, dict[str, float]]:
        """
        Produce a full action-space probability vector plus compact dict.

        Args:
            root: Root node after search
            temperature: Sampling temperature

        Returns:
            full_probs: NumPy array over full action space
            move_probs: dict mapping move UCI -> probability
        """
        temperature = self.config.temperature if temperature is None else temperature

        full_probs = np.zeros(self.move_encoding.action_size, dtype=np.float32)

        if not root.children:
            return full_probs, {}

        mating_moves = (
            find_mate_in_one(root.board.copy(stack=True))
            if self.config.use_tactical_root_filter
            else []
        )
        if mating_moves:
            probability = 1.0 / len(mating_moves)
            move_probs: dict[str, float] = {}
            for move in mating_moves:
                move_uci = move.uci()
                move_probs[move_uci] = probability
                idx = self.move_encoding.uci_to_index(move_uci, root.board)
                full_probs[idx] = probability
            return full_probs, move_probs

        children = self._root_children_for_action(root)
        visits = np.array([child.visit_count for child in children], dtype=np.float64)

        if temperature <= 1e-8:
            probs = np.zeros_like(visits)
            probs[int(np.argmax(visits))] = 1.0
        else:
            adjusted = visits ** (1.0 / temperature)
            total = adjusted.sum()
            if total <= 0:
                probs = np.full_like(adjusted, 1.0 / len(adjusted))
            else:
                probs = adjusted / total

        move_probs: dict[str, float] = {}
        for child, prob in zip(children, probs):
            move_uci = child.move.uci()
            move_probs[move_uci] = float(prob)
            idx = self.move_encoding.uci_to_index(move_uci, root.board)
            full_probs[idx] = float(prob)

        return full_probs, move_probs
