"""
Generates self-play games for AlphaZero-style learning.

Each game produces training samples of the form:
- encoded board state
- MCTS policy target over full action space
- final game value from the player's perspective at that state
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

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
    ended_by_resignation: bool = False
    ended_by_adjudication: bool = False


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
        max_moves: int = 300,
        opening_temperature_moves: int = 20,
        opening_temperature: float = 1.5,
        late_temperature: float = 0.3,
        resign_threshold: float = -0.80,
        min_moves_before_resign: int = 30,
        adjudicate_on_max_moves: bool = True,
        adjudication_threshold: float = 0.10,
    ) -> None:
        self.inference = inference
        self.move_encoding = move_encoding
        self.encoder = encoder or BoardEncoder()
        self.mcts_config = mcts_config or MCTSConfig()

        self.max_moves = max_moves
        self.opening_temperature_moves = opening_temperature_moves
        self.opening_temperature = opening_temperature
        self.late_temperature = late_temperature

        self.resign_threshold = resign_threshold
        self.min_moves_before_resign = min_moves_before_resign

        self.adjudicate_on_max_moves = adjudicate_on_max_moves
        self.adjudication_threshold = adjudication_threshold

    def _result_to_white_value(self, result: str) -> float:
        if result == "1-0":
            return 1.0
        if result == "0-1":
            return -1.0
        return 0.0

    def _temperature_for_move(self, move_number: int) -> float:
        if move_number < self.opening_temperature_moves:
            return self.opening_temperature
        return self.late_temperature

    def _value_to_white_perspective(
        self,
        board: chess.Board,
        side_to_move_value: float,
    ) -> float:
        return side_to_move_value if board.turn == chess.WHITE else -side_to_move_value

    def _resignation_result(self, board: chess.Board) -> str:
        return "0-1" if board.turn == chess.WHITE else "1-0"

    def _material_score_white(self, board: chess.Board) -> int:
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0,
        }

        score = 0
        for piece_type, value in piece_values.items():
            score += len(board.pieces(piece_type, chess.WHITE)) * value
            score -= len(board.pieces(piece_type, chess.BLACK)) * value
        return score

    def _adjudicate_result(self, board: chess.Board) -> str:
        """
        Use both model evaluation and material balance when max_moves is reached.
        """
        _, side_to_move_value = self.inference.predict(board)
        white_value = self._value_to_white_perspective(board, side_to_move_value)
        material_score = self._material_score_white(board)

        if white_value >= self.adjudication_threshold and material_score >= 3:
            return "1-0"
        if white_value <= -self.adjudication_threshold and material_score <= -3:
            return "0-1"
        return "1/2-1/2"

    def play_game(self) -> SelfPlayGameResult:
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

        ended_by_resignation = False
        ended_by_adjudication = False
        forced_result: Optional[str] = None

        move_number = 0
        while not board.is_game_over() and move_number < self.max_moves:
            encoded_state = self.encoder.encode(board)
            root = mcts.run(board)

            temperature = self._temperature_for_move(move_number)
            full_probs, _ = mcts.get_action_probs(root, temperature=temperature)

            estimated_value = root.q_value

            if (
                move_number >= self.min_moves_before_resign
                and estimated_value <= self.resign_threshold
            ):
                forced_result = self._resignation_result(board)
                ended_by_resignation = True
                break

            move = mcts.select_action(root, temperature=temperature)

            history_states.append(encoded_state)
            history_policy_targets.append(full_probs.astype(np.float32))
            history_players.append(board.turn)
            moves_played.append(move.uci())

            board.push(move)
            move_number += 1

        if forced_result is not None:
            result = forced_result
        elif board.is_game_over():
            result = board.result(claim_draw=True)
        else:
            if self.adjudicate_on_max_moves:
                result = self._adjudicate_result(board)
                ended_by_adjudication = True
            else:
                result = "1/2-1/2"

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
            ended_by_resignation=ended_by_resignation,
            ended_by_adjudication=ended_by_adjudication,
        )

    def generate_games(self, num_games: int) -> List[SelfPlayGameResult]:
        return [self.play_game() for _ in range(num_games)]
