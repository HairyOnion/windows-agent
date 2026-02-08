from __future__ import annotations

import tkinter as tk
from pathlib import Path


class LogViewer:
    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.root = tk.Tk()
        self.root.title("IntegrateAgent Logs")
        self.root.geometry("800x500")

        self.text = tk.Text(self.root, wrap="none")
        self.text.pack(fill="both", expand=True)

        self._poll()

    def _read_tail(self, n: int = 300) -> str:
        if not self.log_path.exists():
            return "<log file does not exist yet>"
        with self.log_path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[-n:]
        return "".join(lines)

    def _poll(self) -> None:
        content = self._read_tail()
        self.text.delete("1.0", "end")
        self.text.insert("end", content)
        self.text.see("end")
        self.root.after(1000, self._poll)

    def run(self) -> None:
        self.root.mainloop()
