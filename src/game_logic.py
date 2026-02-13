from __future__ import annotations

import random
import time
from collections import deque

from models import GameState


class GameEngine:
    def __init__(self, rows: int, cols: int, mine_count: int, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self.state = GameState(rows=rows, cols=cols, mine_count=mine_count)

    def reset(self, rows: int | None = None, cols: int | None = None, mine_count: int | None = None) -> None:
        self.state = GameState(
            rows=rows if rows is not None else self.state.rows,
            cols=cols if cols is not None else self.state.cols,
            mine_count=mine_count if mine_count is not None else self.state.mine_count,
        )

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.state.rows and 0 <= c < self.state.cols

    def neighbors(self, r: int, c: int) -> list[tuple[int, int]]:
        result: list[tuple[int, int]] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc):
                    result.append((nr, nc))
        return result

    def _place_mines(self, safe_r: int, safe_c: int) -> None:
        candidates = [
            (r, c)
            for r in range(self.state.rows)
            for c in range(self.state.cols)
            if not (r == safe_r and c == safe_c)
        ]
        mines = self._rng.sample(candidates, self.state.mine_count)
        for r, c in mines:
            self.state.board[r][c].is_mine = True

        for r in range(self.state.rows):
            for c in range(self.state.cols):
                if self.state.board[r][c].is_mine:
                    continue
                self.state.board[r][c].adjacent_mines = sum(
                    1 for nr, nc in self.neighbors(r, c) if self.state.board[nr][nc].is_mine
                )

    def toggle_mark(self, r: int, c: int) -> None:
        cell = self.state.board[r][c]
        if self.state.is_game_over or self.state.is_cleared or cell.is_open:
            return

        if not cell.is_flagged and not cell.is_question:
            cell.is_flagged = True
            self.state.flags_count += 1
        elif cell.is_flagged:
            cell.is_flagged = False
            cell.is_question = True
            self.state.flags_count -= 1
        else:
            cell.is_question = False

    def open_cell(self, r: int, c: int) -> None:
        if self.state.is_game_over or self.state.is_cleared:
            return

        cell = self.state.board[r][c]
        if cell.is_open:
            self._open_neighbors_if_marked(r, c)
            return

        if cell.is_flagged:
            return

        if self.state.is_first_click:
            self._place_mines(r, c)
            self.state.is_first_click = False
            self.state.start_time = time.time()

        if cell.is_mine:
            cell.is_open = True
            self.state.is_game_over = True
            return

        self._open_flood(r, c)
        self._check_clear()

    def _open_neighbors_if_marked(self, r: int, c: int) -> None:
        cell = self.state.board[r][c]
        if cell.adjacent_mines == 0:
            return

        neighbors = self.neighbors(r, c)
        flagged_count = sum(1 for nr, nc in neighbors if self.state.board[nr][nc].is_flagged)
        if flagged_count != cell.adjacent_mines:
            return

        for nr, nc in neighbors:
            target = self.state.board[nr][nc]
            if target.is_open or target.is_flagged:
                continue
            if target.is_mine:
                target.is_open = True
                self.state.is_game_over = True
                return
            self._open_flood(nr, nc)

        self._check_clear()

    def _open_flood(self, r: int, c: int) -> None:
        queue: deque[tuple[int, int]] = deque([(r, c)])
        while queue:
            cr, cc = queue.popleft()
            current = self.state.board[cr][cc]
            if current.is_open or current.is_flagged:
                continue
            current.is_open = True
            current.is_question = False
            if current.adjacent_mines != 0:
                continue
            for nr, nc in self.neighbors(cr, cc):
                nxt = self.state.board[nr][nc]
                if not nxt.is_open and not nxt.is_flagged:
                    queue.append((nr, nc))

    def reveal_all_mines(self) -> None:
        for row in self.state.board:
            for cell in row:
                if cell.is_mine:
                    cell.is_open = True

    def _check_clear(self) -> None:
        opened = sum(1 for row in self.state.board for cell in row if cell.is_open)
        target = self.state.rows * self.state.cols - self.state.mine_count
        if opened == target:
            self.state.is_cleared = True

    def elapsed_seconds(self) -> int:
        if self.state.start_time is None:
            return self.state.elapsed_seconds
        if self.state.is_game_over or self.state.is_cleared:
            return self.state.elapsed_seconds
        return min(999, int(time.time() - self.state.start_time))

    def freeze_timer(self) -> None:
        self.state.elapsed_seconds = self.elapsed_seconds()
