from __future__ import annotations

DIFFICULTY_PRESETS: dict[str, tuple[int, int, int]] = {
    "初級": (9, 9, 10),
    "中級": (16, 16, 40),
    "上級": (16, 30, 99),
}

NUMBER_COLORS: dict[int, str] = {
    1: "blue",
    2: "green",
    3: "red",
    4: "navy",
    5: "brown",
    6: "cyan4",
    7: "black",
    8: "gray40",
}

MIN_ROWS = 5
MAX_ROWS = 30
MIN_COLS = 5
MAX_COLS = 50
