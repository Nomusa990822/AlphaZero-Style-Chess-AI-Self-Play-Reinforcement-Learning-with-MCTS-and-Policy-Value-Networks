import chess

from src.mcts.node import MCTSNode


def test_node_initial_state():
    board = chess.Board()
    node = MCTSNode(board=board)

    assert node.visit_count == 0
    assert node.value_sum == 0.0
    assert node.q_value == 0.0
    assert not node.expanded()
    assert node.children == {}


def test_node_expand_creates_children():
    board = chess.Board()
    node = MCTSNode(board=board)

    priors = {move.uci(): 1 / 20 for move in board.legal_moves}
    node.expand(priors)

    assert node.expanded()
    assert len(node.children) == 20
    assert "e2e4" in node.children


def test_child_board_after_expand():
    board = chess.Board()
    node = MCTSNode(board=board)

    priors = {move.uci(): 1 / 20 for move in board.legal_moves}
    node.expand(priors)

    child = node.children["e2e4"]
    assert child.move.uci() == "e2e4"
    assert child.board.turn == chess.BLACK


def test_terminal_value_white_win_for_side_to_move_loss():
    board = chess.Board()
    board.push_uci("f2f3")
    board.push_uci("e7e5")
    board.push_uci("g2g4")
    board.push_uci("d8h4")  # checkmate, white to move and lost

    node = MCTSNode(board=board)
    assert node.is_terminal()
    assert node.terminal_value() == -1.0


def test_terminal_value_draw():
    board = chess.Board("7k/5Q2/7K/8/8/8/8/8 b - - 0 1")
    node = MCTSNode(board=board)

    assert node.is_terminal()
    assert node.terminal_value() == 0.0


def test_visit_distribution():
    board = chess.Board()
    node = MCTSNode(board=board)

    priors = {move.uci(): 1 / 20 for move in board.legal_moves}
    node.expand(priors)

    node.children["e2e4"].visit_count = 30
    node.children["d2d4"].visit_count = 10

    dist = node.get_visit_distribution()

    assert abs(sum(dist.values()) - 1.0) < 1e-9
    assert dist["e2e4"] > dist["d2d4"]


def test_claimable_threefold_repetition_is_terminal_draw():
    board = chess.Board()
    for move in ("g1f3", "g8f6", "f3g1", "f6g8",
                 "g1f3", "g8f6", "f3g1", "f6g8"):
        board.push_uci(move)

    node = MCTSNode(board=board)

    assert node.is_terminal()
    assert node.terminal_value() == 0.0
