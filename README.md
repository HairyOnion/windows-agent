# IntegrateAgent

Windows-only Python 3.11 project with a FastAPI server and a system tray app that controls it.

## Setup
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -e .
```

3. Set the token:

```powershell
$env:AGENT_TOKEN = "your-token"
```

## Run (Tray App)
Use pythonw to avoid a console window:

```powershell
pythonw -m tray.tray_app
```

The tray icon shows running status and provides controls.

## Quick Run (cmd.exe helpers)
From repo root in `cmd.exe`:

```bat
scripts\setup_windows.cmd
```

Edit `.env` and set `AGENT_TOKEN`, then run:

```bat
scripts\run_tray.cmd
```

Optional (run API server directly without tray):

```bat
scripts\run_server.cmd
```

## API
Health:

```bash
curl http://127.0.0.1:8765/health
```

Command:

```bash
curl -X POST http://127.0.0.1:8765/command \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d "{\"request_id\":\"1\",\"action\":\"run_app\",\"payload\":{\"app\":\"notepad\"}}"
```

## Voicemeeter (Potato)
Voicemeeter controls are exposed as new actions. Targets are `strip-0`..`strip-7` and `bus-0`..`bus-4`.
Gain is restricted to -60.0 through 12.0 and mute is boolean. Raw parameter access is disabled unless allowlisted.

Apply multiple settings:

```bash
curl -X POST http://127.0.0.1:8765/command \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d "{\"request_id\":\"10\",\"action\":\"voicemeeter_apply\",\"payload\":{\"settings\":{\"strip-0\":{\"gain\":-6.0},\"strip-2\":{\"gain\":-60.0},\"bus-0\":{\"gain\":0.0},\"bus-1\":{\"gain\":0.0},\"bus-2\":{\"gain\":0.0}}}}"
```

Group bus gain (bus 0-2):

```bash
curl -X POST http://127.0.0.1:8765/command \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d "{\"request_id\":\"11\",\"action\":\"voicemeeter_group_bus_gain\",\"payload\":{\"gain\":-3.0}}"
```

Reset or restart:

```bash
curl -X POST http://127.0.0.1:8765/command \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d "{\"request_id\":\"12\",\"action\":\"voicemeeter_command\",\"payload\":{\"command\":\"reset\"}}"
```

Read current values:

```bash
curl -X POST http://127.0.0.1:8765/command \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d "{\"request_id\":\"13\",\"action\":\"voicemeeter_get\",\"payload\":{\"targets\":[\"strip-0\",\"strip-1\"],\"fields\":[\"gain\",\"mute\"]}}"
```

Raw parameter access (disabled by default, enable allowlist in `server/config.py`):

```bash
curl -X POST http://127.0.0.1:8765/command \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d "{\"request_id\":\"14\",\"action\":\"voicemeeter_set\",\"payload\":{\"params\":[{\"param\":\"Strip[0].Mute\",\"value\":true}]}}"
```

```bash
curl -X POST http://127.0.0.1:8765/command \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d "{\"request_id\":\"15\",\"action\":\"voicemeeter_get\",\"payload\":{\"params\":[{\"param\":\"Strip[0].Mute\"}]}}"
```

## Notes
- Server binds to 127.0.0.1:8765 by default.
- Authorization is required for `/command`.
- App allowlist and key allowlist are in `server/config.py`.
- Voicemeeter allowlists are in `server/config.py`.
- Logs are stored in `%APPDATA%\\IntegrateAgent\\logs\\agent.log`.
