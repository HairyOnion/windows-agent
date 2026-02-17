from __future__ import annotations

import datetime as dt
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
SERVER_OUTPUT_LOG_FILE = LOG_DIR / "server_output.log"
ENV_FILE = BASE_DIR / ".env"
ENV_SERVER_OUTPUT_LOG_ENABLED = "TRAY_SERVER_OUTPUT_LOG_ENABLED"
ENV_SERVER_OUTPUT_LOG_DAILY_CLEAR = "TRAY_SERVER_OUTPUT_LOG_DAILY_CLEAR"

SERVER_URL = "http://127.0.0.1:8765/health"


class TrayApp:
    def __init__(self) -> None:
        self.icon = pystray.Icon("IntegrateAgent")
        self.icon.icon = Image.open(ICON_BAD)
        self.server_proc: Optional[subprocess.Popen] = None
        self.server_log_handle = None
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
        self.server_proc = None
        self._close_server_log_handle()
        self._load_env_from_file()
        logging_enabled = self._env_bool(ENV_SERVER_OUTPUT_LOG_ENABLED, default=False)
        daily_clear_enabled = self._env_bool(ENV_SERVER_OUTPUT_LOG_DAILY_CLEAR, default=True)
        stdout_target = subprocess.DEVNULL
        stderr_target = subprocess.DEVNULL
        if logging_enabled:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            self.server_log_handle = self._open_server_log_handle(daily_clear_enabled=daily_clear_enabled)
            stdout_target = self.server_log_handle
            stderr_target = subprocess.STDOUT
        python_exe = sys.executable
        cmd = [
            python_exe,
            "-m",
            "uvicorn",
            "server.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8765",
        ]
        self.server_proc = subprocess.Popen(
            cmd,
            cwd=str(BASE_DIR),
            env=os.environ.copy(),
            stdout=stdout_target,
            stderr=stderr_target,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    def stop_server(self, _icon=None, _item=None) -> None:
        if self.server_proc and self.server_proc.poll() is None:
            self.server_proc.terminate()
            try:
                self.server_proc.wait(timeout=5)
            except Exception:
                self.server_proc.kill()
        self.server_proc = None
        self._close_server_log_handle()

    def _close_server_log_handle(self) -> None:
        if self.server_log_handle:
            self.server_log_handle.close()
            self.server_log_handle = None

    def _open_server_log_handle(self, daily_clear_enabled: bool):
        mode = "a"
        if daily_clear_enabled and SERVER_OUTPUT_LOG_FILE.exists():
            last_modified = dt.date.fromtimestamp(SERVER_OUTPUT_LOG_FILE.stat().st_mtime)
            if last_modified < dt.date.today():
                mode = "w"
        return SERVER_OUTPUT_LOG_FILE.open(mode, encoding="utf-8")

    def _env_bool(self, name: str, default: bool) -> bool:
        raw = os.environ.get(name)
        if raw is None:
            return default
        value = raw.strip().lower()
        if value in {"1", "true", "yes", "on"}:
            return True
        if value in {"0", "false", "no", "off"}:
            return False
        return default

    def _load_env_from_file(self) -> None:
        if not ENV_FILE.exists():
            return
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            raw = line.strip()
            if not raw or raw.startswith("#") or "=" not in raw:
                continue
            key, value = raw.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ.setdefault(key, value)

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
        # Keep tray startup behavior aligned with scripts/run_server.cmd:
        # launching the tray should also bring up the API server.
        self.start_server()
        threading.Thread(target=self._poll_health, daemon=True).start()
        self.icon.run()


def main() -> None:
    TrayApp().run()


if __name__ == "__main__":
    main()
