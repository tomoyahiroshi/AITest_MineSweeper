from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from game_logic import GameEngine


def test_first_click_safe() -> None:
    engine = GameEngine(9, 9, 10, seed=1)
    engine.open_cell(0, 0)
    assert not engine.state.board[0][0].is_mine


def test_mine_count_matches() -> None:
    engine = GameEngine(9, 9, 10, seed=1)
    engine.open_cell(1, 1)
    mines = sum(1 for row in engine.state.board for cell in row if cell.is_mine)
    assert mines == 10


def test_adjacent_mines_count() -> None:
    engine = GameEngine(5, 5, 3, seed=1)
    engine.open_cell(2, 2)
    for r in range(engine.state.rows):
        for c in range(engine.state.cols):
            cell = engine.state.board[r][c]
            if cell.is_mine:
                continue
            expected = sum(
                1
                for nr, nc in engine.neighbors(r, c)
                if engine.state.board[nr][nc].is_mine
            )
            assert cell.adjacent_mines == expected


def test_zero_flood_open() -> None:
    engine = GameEngine(5, 5, 1, seed=2)
    engine.open_cell(0, 0)
    opened = sum(1 for row in engine.state.board for cell in row if cell.is_open)
    assert opened > 1


def test_clear_condition() -> None:
    engine = GameEngine(5, 5, 1, seed=3)
    engine.open_cell(0, 0)
    for r in range(engine.state.rows):
        for c in range(engine.state.cols):
            cell = engine.state.board[r][c]
            if not cell.is_mine:
                engine.open_cell(r, c)
    assert engine.state.is_cleared


def test_open_neighbors_when_number_cell_clicked() -> None:
    engine = GameEngine(3, 3, 1)
    state = engine.state
    state.is_first_click = False

    state.board[0][0].is_mine = True
    for r in range(state.rows):
        for c in range(state.cols):
            cell = state.board[r][c]
            if cell.is_mine:
                continue
            cell.adjacent_mines = sum(
                1 for nr, nc in engine.neighbors(r, c) if state.board[nr][nc].is_mine
            )

    state.board[1][1].is_open = True
    state.board[0][0].is_flagged = True

    engine.open_cell(1, 1)

    assert state.board[0][1].is_open
    assert state.board[1][0].is_open
    assert not state.is_game_over
