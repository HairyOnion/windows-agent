# IntegrateAgent Design Contract

## Purpose
IntegrateAgent is a Windows-only local automation agent that exposes a minimal, authenticated HTTP API for launching allowlisted applications, sending allowlisted keypress combinations, and controlling Voicemeeter Potato through allowlisted actions.

## Architecture
- Two-process design:
  - FastAPI server (local HTTP API).
  - Windows system tray controller (pystray) that starts/stops and monitors the server.
- The tray app launches the server as a subprocess and updates its icon based on `/health`.

## Security Model
- Local-only binding: server binds to `127.0.0.1:8765` by default.
- Bearer token authentication for `/command` via `Authorization: Bearer <TOKEN>`.
- Token comes from `AGENT_TOKEN` environment variable; server refuses to start if missing.
- Strict allowlists for `run_app`, `key_press`, and Voicemeeter actions.
- No arbitrary execution, no shell invocation, no remote binding.

## Supported Actions
- `run_app`: Launches an allowlisted application (absolute path) with allowlisted args. Uses `subprocess.Popen` with `shell=False`.
- `key_press`: Sends allowlisted key sequences via `pynput`. Modifier keys (ctrl/alt/shift/win/cmd) are pressed and held first, non-modifiers are pressed/released while held, then modifiers are released in reverse order.
- `voicemeeter_apply`: Applies allowlisted settings to Voicemeeter targets (`strip-*`, `bus-*`).
- `voicemeeter_group_bus_gain`: Applies a single gain value to buses 0-2.
- `voicemeeter_command`: Executes allowlisted Voicemeeter commands (`reset`, `restart`).
- `voicemeeter_get`: Reads allowlisted target fields or allowlisted raw parameters.
- `voicemeeter_set`: Writes allowlisted raw parameters.

## Logging
- JSON line logging via rotating file handler.
- Path: `%APPDATA%\IntegrateAgent\logs\agent.log`.
- Logs include `request_id`, `action`, `ok`, `error`, `caller_ip`, `timestamp_utc`, plus startup/shutdown events.

## Configuration
- Environment:
  - `AGENT_TOKEN` (required for server start).
- Allowlists and defaults:
  - App allowlist in `server/config.py` (`BASE_ALLOWLIST`).
  - Key allowlist in `server/config.py` (`ALLOWED_KEYS`).
  - Voicemeeter allowlists in `server/config.py` (`VOICEMEETER_*`).
  - Host/port/version in `server/config.py`.

## Non-Goals / Out of Scope
- Remote access or listening on non-local interfaces.
- Arbitrary command execution or shell access.
- Dynamic allowlist changes via API.
- Macro recording or scripting engine.

## Rules for Future Changes
- Preserve the two-process architecture (server + tray controller).
- Do not weaken security: keep localhost binding, bearer auth, and allowlists mandatory.
- Any new actions must be explicitly allowlisted and validated.
