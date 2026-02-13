from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Cell:
    is_mine: bool = False
    is_open: bool = False
    is_flagged: bool = False
    is_question: bool = False
    adjacent_mines: int = 0


@dataclass
class GameState:
    rows: int
    cols: int
    mine_count: int
    board: list[list[Cell]] = field(default_factory=list)
    is_first_click: bool = True
    is_game_over: bool = False
    is_cleared: bool = False
    elapsed_seconds: int = 0
    flags_count: int = 0
    start_time: float | None = None

    def __post_init__(self) -> None:
        if not self.board:
            self.board = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]
