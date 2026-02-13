from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog

from config import (
    DIFFICULTY_PRESETS,
    MAX_COLS,
    MAX_ROWS,
    MIN_COLS,
    MIN_ROWS,
    NUMBER_COLORS,
)
from game_logic import GameEngine


class MineSweeperApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Minesweeper")
        rows, cols, mines = DIFFICULTY_PRESETS["初級"]
        self.engine = GameEngine(rows, cols, mines)

        self.mines_var = tk.StringVar(value=f"💣 {mines}")
        self.timer_var = tk.StringVar(value="⏱ 0")
        self.face_var = tk.StringVar(value="🙂")
        self.buttons: list[list[tk.Button]] = []

        self._build_menu()
        self._build_layout()
        self._build_board()
        self.root.bind("<Configure>", self.on_window_resize)
        self._tick_timer()

    def _build_menu(self) -> None:
        menu = tk.Menu(self.root)
        game_menu = tk.Menu(menu, tearoff=False)
        game_menu.add_command(label="新規", command=self.reset_game)
        for name in DIFFICULTY_PRESETS:
            game_menu.add_command(label=name, command=lambda n=name: self.set_difficulty(n))
        game_menu.add_command(label="カスタム", command=self.set_custom)
        game_menu.add_separator()
        game_menu.add_command(label="終了", command=self.root.destroy)
        menu.add_cascade(label="ゲーム", menu=game_menu)

        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="操作方法", command=self.show_help)
        help_menu.add_command(label="バージョン情報", command=lambda: messagebox.showinfo("Version", "v0.1"))
        menu.add_cascade(label="ヘルプ", menu=help_menu)
        self.root.config(menu=menu)

    def _build_layout(self) -> None:
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.top = tk.Frame(self.root, padx=8, pady=8)
        self.top.pack(fill=tk.X)
        tk.Label(self.top, textvariable=self.mines_var, width=10).pack(side=tk.LEFT)
        tk.Button(self.top, textvariable=self.face_var, width=4, command=self.reset_game).pack(side=tk.LEFT, padx=8)
        tk.Label(self.top, textvariable=self.timer_var, width=8).pack(side=tk.RIGHT)

        self.board_frame = tk.Frame(self.root, padx=8, pady=8)
        self.board_frame.pack(fill=tk.BOTH, expand=True)

    def _build_board(self) -> None:
        for w in self.board_frame.winfo_children():
            w.destroy()

        s = self.engine.state
        self.buttons = []
        for r in range(s.rows):
            row_buttons: list[tk.Button] = []
            self.board_frame.rowconfigure(r, weight=1, uniform="row")
            for c in range(s.cols):
                self.board_frame.columnconfigure(c, weight=1, uniform="col")
                btn = tk.Button(self.board_frame, width=2, height=1, relief=tk.RAISED)
                btn.grid(row=r, column=c, sticky="nsew")
                btn.bind("<Button-1>", lambda e, rr=r, cc=c: self.on_left_click(rr, cc))
                btn.bind("<Button-3>", lambda e, rr=r, cc=c: self.on_right_click(rr, cc))
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        self.update_all_cells()

    def on_window_resize(self, event: tk.Event[tk.Misc]) -> None:
        if event.widget is not self.root or not self.buttons:
            return

        board_width = self.board_frame.winfo_width()
        board_height = self.board_frame.winfo_height()
        rows = self.engine.state.rows
        cols = self.engine.state.cols
        if rows == 0 or cols == 0:
            return

        cell_size = min(board_width // cols, board_height // rows)
        font_size = max(8, min(16, int(cell_size * 0.45)))
        for row in self.buttons:
            for btn in row:
                btn.config(font=("", font_size))

    def on_left_click(self, r: int, c: int) -> None:
        if self.engine.state.is_game_over or self.engine.state.is_cleared:
            return
        self.engine.open_cell(r, c)
        if self.engine.state.is_game_over:
            self.engine.freeze_timer()
            self.engine.reveal_all_mines()
            self.face_var.set("😵")
            self.update_all_cells()
            self.root.after(0, lambda: messagebox.showinfo("ゲームオーバー", "地雷を踏みました"))
            return
        elif self.engine.state.is_cleared:
            self.engine.freeze_timer()
            self.face_var.set("😎")
            self.update_all_cells()
            self.root.after(0, lambda: messagebox.showinfo("クリア", "おめでとうございます"))
            return
        self.update_all_cells()

    def on_right_click(self, r: int, c: int) -> None:
        self.engine.toggle_mark(r, c)
        self.update_all_cells()

    def update_all_cells(self) -> None:
        s = self.engine.state
        self.mines_var.set(f"💣 {s.mine_count - s.flags_count}")
        self.timer_var.set(f"⏱ {self.engine.elapsed_seconds()}")

        for r in range(s.rows):
            for c in range(s.cols):
                cell = s.board[r][c]
                btn = self.buttons[r][c]
                if cell.is_open:
                    btn.config(relief=tk.FLAT, state=tk.DISABLED)
                    if cell.is_mine:
                        btn.config(text="💣", bg="tomato" if s.is_game_over else "SystemButtonFace")
                    elif cell.adjacent_mines == 0:
                        btn.config(text="", bg="SystemButtonFace")
                    else:
                        btn.config(text=str(cell.adjacent_mines), fg=NUMBER_COLORS[cell.adjacent_mines], bg="SystemButtonFace")
                else:
                    btn.config(relief=tk.RAISED, state=tk.NORMAL, bg="SystemButtonFace", fg="black")
                    if cell.is_flagged:
                        btn.config(text="🚩")
                    elif cell.is_question:
                        btn.config(text="?")
                    else:
                        btn.config(text="")

    def _tick_timer(self) -> None:
        self.timer_var.set(f"⏱ {self.engine.elapsed_seconds()}")
        self.root.after(1000, self._tick_timer)

    def reset_game(self) -> None:
        s = self.engine.state
        self.engine.reset(s.rows, s.cols, s.mine_count)
        self.face_var.set("🙂")
        self._build_board()

    def set_difficulty(self, name: str) -> None:
        rows, cols, mines = DIFFICULTY_PRESETS[name]
        self.engine.reset(rows, cols, mines)
        self.face_var.set("🙂")
        self._build_board()

    def set_custom(self) -> None:
        rows = simpledialog.askinteger("カスタム", f"行数 ({MIN_ROWS}-{MAX_ROWS})", parent=self.root)
        cols = simpledialog.askinteger("カスタム", f"列数 ({MIN_COLS}-{MAX_COLS})", parent=self.root)
        mines = simpledialog.askinteger("カスタム", "地雷数", parent=self.root)
        if rows is None or cols is None or mines is None:
            return
        if not (MIN_ROWS <= rows <= MAX_ROWS and MIN_COLS <= cols <= MAX_COLS and 1 <= mines <= rows * cols - 1):
            messagebox.showerror("入力エラー", "範囲外の値です")
            return
        self.engine.reset(rows, cols, mines)
        self.face_var.set("🙂")
        self._build_board()

    @staticmethod
    def show_help() -> None:
        messagebox.showinfo(
            "操作方法",
            "左クリック: 開く\n右クリック: 旗→?→未設定\n目的: 地雷を避けてすべての安全マスを開く",
        )
