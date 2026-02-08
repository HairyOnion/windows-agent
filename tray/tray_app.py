from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

import pystray
import requests
from PIL import Image

from .log_viewer import LogViewer


BASE_DIR = Path(__file__).resolve().parents[1]
ICON_OK = Path(__file__).resolve().parent / "icons" / "status_ok.png"
ICON_BAD = Path(__file__).resolve().parent / "icons" / "status_bad.png"
LOG_DIR = Path(os.environ.get("APPDATA", r"C:\\")) / "IntegrateAgent" / "logs"
LOG_FILE = LOG_DIR / "agent.log"

SERVER_URL = "http://127.0.0.1:8765/health"


class TrayApp:
    def __init__(self) -> None:
        self.icon = pystray.Icon("IntegrateAgent")
        self.icon.icon = Image.open(ICON_BAD)
        self.server_proc: Optional[subprocess.Popen] = None
        self._stop_event = threading.Event()

        self.icon.menu = pystray.Menu(
            pystray.MenuItem("Start Server", self.start_server),
            pystray.MenuItem("Stop Server", self.stop_server),
            pystray.MenuItem("Open Log Window", self.open_log_window),
            pystray.MenuItem("Open Log File Location", self.open_log_location),
            pystray.MenuItem("Exit", self.exit_app),
        )

    def start_server(self, _icon=None, _item=None) -> None:
        if self.server_proc and self.server_proc.poll() is None:
            return
        python_exe = sys.executable
        cmd = [
            python_exe,
            "-m",
            "uvicorn",
            "server.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8765",
        ]
        self.server_proc = subprocess.Popen(
            cmd,
            cwd=str(BASE_DIR),
            env=os.environ.copy(),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    def stop_server(self, _icon=None, _item=None) -> None:
        if not self.server_proc or self.server_proc.poll() is not None:
            return
        self.server_proc.terminate()
        try:
            self.server_proc.wait(timeout=5)
        except Exception:
            self.server_proc.kill()

    def open_log_window(self, _icon=None, _item=None) -> None:
        viewer = LogViewer(LOG_FILE)
        threading.Thread(target=viewer.run, daemon=True).start()

    def open_log_location(self, _icon=None, _item=None) -> None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(["explorer", str(LOG_DIR)], shell=False)

    def exit_app(self, _icon=None, _item=None) -> None:
        self._stop_event.set()
        self.stop_server()
        self.icon.stop()

    def _poll_health(self) -> None:
        while not self._stop_event.is_set():
            ok = False
            try:
                resp = requests.get(SERVER_URL, timeout=1)
                ok = resp.status_code == 200
            except Exception:
                ok = False
            self.icon.icon = Image.open(ICON_OK if ok else ICON_BAD)
            time.sleep(2)

    def run(self) -> None:
        threading.Thread(target=self._poll_health, daemon=True).start()
        self.icon.run()


def main() -> None:
    TrayApp().run()


if __name__ == "__main__":
    main()
