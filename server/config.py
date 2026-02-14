from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set
import os


@dataclass(frozen=True)
class AppAllowlistEntry:
    name: str
    path: Path
    allowed_args_patterns: List[str]


BASE_ALLOWLIST: Dict[str, AppAllowlistEntry] = {
    "notepad": AppAllowlistEntry(
        name="notepad",
        path=Path(r"C:\\Windows\\System32\\notepad.exe"),
        allowed_args_patterns=[r".*"],
    ),
}

ALLOWED_KEYS = {
    "enter",
    "esc",
    "tab",
    "space",
    "backspace",
    "delete",
    "left",
    "right",
    "up",
    "down",
    "home",
    "end",
    "page_up",
    "page_down",
    "f1",
    "f2",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "f10",
    "f11",
    "f12",
    "ctrl",
    "alt",
    "shift",
    "cmd",
    "win",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
}

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
VERSION = "0.1.0"

APPDATA_LOG_DIR = Path(os.environ.get("APPDATA", r"C:\\")) / "IntegrateAgent" / "logs"

VOICEMEETER_KIND = "potato"
VOICEMEETER_ALLOWED_STRIPS: Set[int] = set(range(0, 8))
VOICEMEETER_ALLOWED_BUSES: Set[int] = set(range(0, 5))
VOICEMEETER_ALLOWED_TARGET_PATTERNS = [
    r"strip-\d+",
    r"bus-\d+",
]
VOICEMEETER_ALLOWED_FIELD_PATTERNS = [
    r"gain",
    r"mute",
]
VOICEMEETER_ALLOWED_COMMANDS = {
    "reset",
    "restart",
}
VOICEMEETER_ALLOWED_PARAM_PATTERNS: List[str] = []
VOICEMEETER_GAIN_MIN = -60.0
VOICEMEETER_GAIN_MAX = 12.0
VOICEMEETER_GROUP_BUS_IDS = [0, 1, 2]

