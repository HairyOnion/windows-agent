from __future__ import annotations

import re
from threading import Lock
from typing import Any, Dict, Iterable, List, Tuple

from .config import (
    VOICEMEETER_ALLOWED_BUSES,
    VOICEMEETER_ALLOWED_COMMANDS,
    VOICEMEETER_ALLOWED_FIELD_PATTERNS,
    VOICEMEETER_ALLOWED_PARAM_PATTERNS,
    VOICEMEETER_ALLOWED_STRIPS,
    VOICEMEETER_ALLOWED_TARGET_PATTERNS,
    VOICEMEETER_GAIN_MAX,
    VOICEMEETER_GAIN_MIN,
    VOICEMEETER_GROUP_BUS_IDS,
    VOICEMEETER_KIND,
)

try:
    import voicemeeterlib
except Exception as exc:  # pragma: no cover - import error path
    voicemeeterlib = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


_VM_LOCK = Lock()
_VM_CLIENT = None
_VM_LOGGED_IN = False


def _require_lib() -> None:
    if voicemeeterlib is None:
        raise RuntimeError(f"voicemeeter-api not available: {_IMPORT_ERROR}")


def _get_vm():
    global _VM_CLIENT, _VM_LOGGED_IN
    _require_lib()
    with _VM_LOCK:
        if _VM_CLIENT is None:
            _VM_CLIENT = voicemeeterlib.api(VOICEMEETER_KIND)
        if not _VM_LOGGED_IN:
            _VM_CLIENT.login()
            _VM_LOGGED_IN = True
    return _VM_CLIENT


def shutdown_vm() -> None:
    global _VM_CLIENT, _VM_LOGGED_IN
    if _VM_CLIENT is None:
        return
    with _VM_LOCK:
        if _VM_CLIENT is not None and _VM_LOGGED_IN:
            try:
                _VM_CLIENT.logout()
            finally:
                _VM_LOGGED_IN = False


def _matches_any(value: str, patterns: Iterable[str]) -> bool:
    return any(re.fullmatch(pattern, value) for pattern in patterns)


def _parse_strip_bus(target: str) -> Tuple[str, int] | None:
    strip_match = re.fullmatch(r"strip-(\d+)", target)
    if strip_match:
        return "strip", int(strip_match.group(1))
    bus_match = re.fullmatch(r"bus-(\d+)", target)
    if bus_match:
        return "bus", int(bus_match.group(1))
    return None


def _validate_target(target: str) -> None:
    if not _matches_any(target, VOICEMEETER_ALLOWED_TARGET_PATTERNS):
        raise ValueError(f"Target not allowed: {target}")
    parsed = _parse_strip_bus(target)
    if not parsed:
        return
    kind, idx = parsed
    if kind == "strip" and idx not in VOICEMEETER_ALLOWED_STRIPS:
        raise ValueError(f"Strip not allowed: {target}")
    if kind == "bus" and idx not in VOICEMEETER_ALLOWED_BUSES:
        raise ValueError(f"Bus not allowed: {target}")


def _flatten_fields(value: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    flat: Dict[str, Any] = {}
    for key, child in value.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(child, dict):
            flat.update(_flatten_fields(child, path))
        else:
            flat[path] = child
    return flat


def _validate_field_paths(paths: Iterable[str]) -> None:
    for path in paths:
        if not _matches_any(path, VOICEMEETER_ALLOWED_FIELD_PATTERNS):
            raise ValueError(f"Field not allowed: {path}")


def _validate_gain_value(value: Any) -> None:
    if not isinstance(value, (int, float)):
        raise ValueError("Gain must be a number")
    if value < VOICEMEETER_GAIN_MIN or value > VOICEMEETER_GAIN_MAX:
        raise ValueError(f"Gain out of range: {value}")


def _validate_mute_value(value: Any) -> None:
    if not isinstance(value, bool):
        raise ValueError("Mute must be a boolean")


def _validate_settings(settings: Dict[str, Dict[str, Any]]) -> None:
    for target, fields in settings.items():
        _validate_target(target)
        flat_fields = _flatten_fields(fields)
        _validate_field_paths(flat_fields.keys())
        for path, value in flat_fields.items():
            if path == "gain":
                _validate_gain_value(value)
            elif path == "mute":
                _validate_mute_value(value)


def apply_settings(settings: Dict[str, Dict[str, Any]]) -> int:
    if not settings:
        raise ValueError("Settings must not be empty")
    _validate_settings(settings)
    vm = _get_vm()
    vm.apply(settings)
    return len(settings)


def apply_group_bus_gain(gain: float) -> Dict[str, Any]:
    _validate_gain_value(gain)
    for bus_id in VOICEMEETER_GROUP_BUS_IDS:
        if bus_id not in VOICEMEETER_ALLOWED_BUSES:
            raise ValueError(f"Bus not allowed: bus-{bus_id}")
    settings = {f"bus-{bus_id}": {"gain": gain} for bus_id in VOICEMEETER_GROUP_BUS_IDS}
    vm = _get_vm()
    vm.apply(settings)
    return {"bus_group": list(VOICEMEETER_GROUP_BUS_IDS), "gain": gain}


def run_command(command: str) -> None:
    if command not in VOICEMEETER_ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {command}")
    vm = _get_vm()
    if command == "reset":
        vm.command.reset()
    elif command == "restart":
        vm.command.restart()
    else:
        raise ValueError(f"Unknown command: {command}")


def _target_object(vm, target: str):
    parsed = _parse_strip_bus(target)
    if not parsed:
        raise ValueError(f"Unsupported target for read: {target}")
    kind, idx = parsed
    if kind == "strip":
        return vm.strip[idx]
    if kind == "bus":
        return vm.bus[idx]
    raise ValueError(f"Unsupported target: {target}")


def get_targets_fields(targets: List[str], fields: List[str]) -> Dict[str, Dict[str, Any]]:
    if not targets:
        raise ValueError("Targets must not be empty")
    if not fields:
        raise ValueError("Fields must not be empty")
    for target in targets:
        _validate_target(target)
    _validate_field_paths(fields)

    field_readers = {
        "gain": lambda obj: obj.gain,
        "mute": lambda obj: obj.mute,
    }
    for field in fields:
        if field not in field_readers:
            raise ValueError(f"Field not supported for read: {field}")

    vm = _get_vm()
    result: Dict[str, Dict[str, Any]] = {}
    for target in targets:
        obj = _target_object(vm, target)
        result[target] = {field: field_readers[field](obj) for field in fields}
    return result


def _validate_param_allowed(param: str) -> None:
    if not VOICEMEETER_ALLOWED_PARAM_PATTERNS:
        raise ValueError("Raw parameter access is disabled")
    if not _matches_any(param, VOICEMEETER_ALLOWED_PARAM_PATTERNS):
        raise ValueError(f"Param not allowed: {param}")


def get_params(params: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not params:
        raise ValueError("Params must not be empty")
    vm = _get_vm()
    values: Dict[str, Any] = {}
    for entry in params:
        param = entry.get("param")
        is_string = bool(entry.get("is_string", False))
        if not param or not isinstance(param, str):
            raise ValueError("Param must be a string")
        _validate_param_allowed(param)
        values[param] = vm.get(param, is_string=is_string)
    return values


def set_params(params: List[Dict[str, Any]]) -> int:
    if not params:
        raise ValueError("Params must not be empty")
    vm = _get_vm()
    for entry in params:
        param = entry.get("param")
        value = entry.get("value")
        if not param or not isinstance(param, str):
            raise ValueError("Param must be a string")
        _validate_param_allowed(param)
        vm.set(param, value)
    return len(params)


