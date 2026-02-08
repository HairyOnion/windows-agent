from __future__ import annotations

from typing import Iterable
from pynput.keyboard import Controller, Key

from .config import ALLOWED_KEYS


KEY_MAP = {
    "enter": Key.enter,
    "esc": Key.esc,
    "tab": Key.tab,
    "space": Key.space,
    "backspace": Key.backspace,
    "delete": Key.delete,
    "left": Key.left,
    "right": Key.right,
    "up": Key.up,
    "down": Key.down,
    "home": Key.home,
    "end": Key.end,
    "page_up": Key.page_up,
    "page_down": Key.page_down,
    "f1": Key.f1,
    "f2": Key.f2,
    "f3": Key.f3,
    "f4": Key.f4,
    "f5": Key.f5,
    "f6": Key.f6,
    "f7": Key.f7,
    "f8": Key.f8,
    "f9": Key.f9,
    "f10": Key.f10,
    "f11": Key.f11,
    "f12": Key.f12,
    "ctrl": Key.ctrl,
    "alt": Key.alt,
    "shift": Key.shift,
    "cmd": Key.cmd,
    "win": Key.cmd,
}


def validate_keys(keys: Iterable[str]) -> None:
    for k in keys:
        if k.lower() not in ALLOWED_KEYS:
            raise ValueError(f"Key not allowed: {k}")


def send_keys(keys: Iterable[str]) -> None:
    controller = Controller()
    modifier_set = {"ctrl", "alt", "shift", "cmd", "win"}
    modifiers: list[str] = []
    non_modifiers: list[str] = []
    seen_mods: set[str] = set()

    for k in keys:
        k_low = k.lower()
        if k_low in modifier_set:
            if k_low not in seen_mods:
                modifiers.append(k_low)
                seen_mods.add(k_low)
        else:
            non_modifiers.append(k_low)

    if not non_modifiers:
        raise ValueError("At least one non-modifier key is required")

    def _press(key_name: str) -> None:
        if key_name in KEY_MAP:
            controller.press(KEY_MAP[key_name])
        else:
            controller.press(key_name)

    def _release(key_name: str) -> None:
        if key_name in KEY_MAP:
            controller.release(KEY_MAP[key_name])
        else:
            controller.release(key_name)

    for m in modifiers:
        _press(m)
    for k in non_modifiers:
        _press(k)
        _release(k)
    for m in reversed(modifiers):
        _release(m)
