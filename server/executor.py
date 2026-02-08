from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import List

from .config import BASE_ALLOWLIST


def _validate_args(args: List[str], patterns: List[str]) -> None:
    for arg in args:
        if not any(re.fullmatch(pat, arg) for pat in patterns):
            raise ValueError(f"Argument not allowed: {arg}")


def run_allowed_app(app_name: str, args: List[str] | None) -> subprocess.Popen:
    entry = BASE_ALLOWLIST.get(app_name)
    if not entry:
        raise ValueError("Unknown app")
    if not entry.path.exists():
        raise ValueError("Configured app path does not exist")

    argv = [str(Path(entry.path))]
    if args:
        _validate_args(args, entry.allowed_args_patterns)
        argv.extend(args)

    return subprocess.Popen(argv, shell=False)
