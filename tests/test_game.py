import chess
import pytest

from src.engine.game import ChessGame


def test_game_starts_in_initial_position():
    game = ChessGame()
    assert game.get_fen().startswith("rnbqkbnr")
    assert game.current_player() == "white"
    assert not game.is_terminal()


def test_game_reset_restores_initial_position():
    game = ChessGame()
    game.push_uci("e2e4")
    game.push_uci("e7e5")
    game.reset()

    assert game.current_player() == "white"
    assert game.move_count() == 0
    assert len(game.legal_moves()) == 20


def test_legal_moves_at_start():
    game = ChessGame()
    legal_moves = game.legal_moves_uci()

    assert len(legal_moves) == 20
    assert "e2e4" in legal_moves
    assert "d2d4" in legal_moves
    assert "g1f3" in legal_moves


def test_push_legal_move_changes_turn():
    game = ChessGame()
    game.push_uci("e2e4")

    assert game.current_player() == "black"
    assert game.move_count() == 1


def test_illegal_move_raises_error():
    game = ChessGame()

    with pytest.raises(ValueError):
        game.push_uci("e2e5")


def test_invalid_uci_raises_error():
    game = ChessGame()

    with pytest.raises(ValueError):
        game.push_uci("notamove")


def test_copy_creates_independent_board():
    game = ChessGame()
    game.push_uci("e2e4")

    clone = game.copy()
    clone.push_uci("e7e5")

    assert game.move_count() == 1
    assert clone.move_count() == 2


def test_fools_mate_checkmate_detection():
    game = ChessGame()
    game.push_uci("f2f3")
    game.push_uci("e7e5")
    game.push_uci("g2g4")
    game.push_uci("d8h4")

    assert game.is_terminal()
    assert game.is_checkmate()
    assert game.result() == "0-1"
    assert game.winner() == "black"


def test_stalemate_detection():
    stalemate_fen = "7k/5Q2/7K/8/8/8/8/8 b - - 0 1"
    game = ChessGame(stalemate_fen)

    assert game.is_terminal()
    assert game.is_stalemate()
    assert game.result() == "1/2-1/2"
    assert game.winner() == "draw"


def test_state_snapshot():
    game = ChessGame()
    state = game.get_state()

    assert state.turn == "white"
    assert state.is_terminal is False
    assert state.result is None
    assert "e2e4" in state.legal_moves
