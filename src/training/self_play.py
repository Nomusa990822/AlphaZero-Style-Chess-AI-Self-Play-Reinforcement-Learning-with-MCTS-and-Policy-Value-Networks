"""
Generates self-play games for AlphaZero-style learning.

Each game produces training samples of the form:
- encoded board state
- MCTS policy target over full action space
- final game value from the player's perspective at that state
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import chess
import numpy as np

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTS, MCTSConfig
from src.model.inference import ModelInference


@dataclass
class SelfPlaySample:
    """
    A single AlphaZero training sample.
    """
    state: np.ndarray
    policy_target: np.ndarray
    value_target: float
    player_to_move: bool


@dataclass
class SelfPlayGameResult:
    """
    Holds one full self-play game and its derived training samples.
    """
    moves: List[str]
    result: str
    samples: List[SelfPlaySample]
    num_positions: int


class SelfPlayGenerator:
    """
    Runs self-play games using MCTS and converts them into training samples.
    """

    def __init__(
        self,
        inference: ModelInference,
        move_encoding: MoveEncoding,
        encoder: BoardEncoder | None = None,
        mcts_config: MCTSConfig | None = None,
        max_moves: int = 200,
        temperature_moves: int = 20,
    ) -> None:
        """
        Args:
            inference: Neural inference helper
            move_encoding: Move encoding helper
            encoder: Board encoder
            mcts_config: MCTS configuration
            max_moves: Safety cap for game length
            temperature_moves: Use temperature=1.0 for early moves,
                               then greedy selection afterward
        """
        self.inference = inference
        self.move_encoding = move_encoding
        self.encoder = encoder or BoardEncoder()
        self.mcts_config = mcts_config or MCTSConfig()
        self.max_moves = max_moves
        self.temperature_moves = temperature_moves

    def _result_to_white_value(self, result: str) -> float:
        """
        Convert result string into scalar from white's perspective.
        """
        if result == "1-0":
            return 1.0
        if result == "0-1":
            return -1.0
        return 0.0

    def play_game(self) -> SelfPlayGameResult:
        """
        Run one self-play game.

        Returns:
            SelfPlayGameResult
        """
        board = chess.Board()
        mcts = MCTS(
            inference=self.inference,
            move_encoding=self.move_encoding,
            config=self.mcts_config,
        )

        history_states: List[np.ndarray] = []
        history_policy_targets: List[np.ndarray] = []
        history_players: List[bool] = []
        moves_played: List[str] = []

        move_number = 0
        while not board.is_game_over() and move_number < self.max_moves:
            encoded_state = self.encoder.encode(board)
            root = mcts.run(board)

            temp = 1.0 if move_number < self.temperature_moves else 0.0
            full_probs, _ = mcts.get_action_probs(root, temperature=temp)
            move = mcts.select_action(root, temperature=temp)

            history_states.append(encoded_state)
            history_policy_targets.append(full_probs.astype(np.float32))
            history_players.append(board.turn)
            moves_played.append(move.uci())

            board.push(move)
            move_number += 1

        result = board.result(claim_draw=True)
        white_value = self._result_to_white_value(result)

        samples: List[SelfPlaySample] = []
        for state, policy_target, player_to_move in zip(
            history_states,
            history_policy_targets,
            history_players,
        ):
            value_target = white_value if player_to_move == chess.WHITE else -white_value

            samples.append(
                SelfPlaySample(
                    state=state,
                    policy_target=policy_target,
                    value_target=float(value_target),
                    player_to_move=player_to_move,
                )
            )

        return SelfPlayGameResult(
            moves=moves_played,
            result=result,
            samples=samples,
            num_positions=len(samples),
        )

    def generate_games(self, num_games: int) -> List[SelfPlayGameResult]:
        """
        Generate multiple self-play games.
        """
        return [self.play_game() for _ in range(num_games)]
