from __future__ import annotations

import tkinter as tk

from ui import MineSweeperApp


def main() -> None:
    root = tk.Tk()
    MineSweeperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
