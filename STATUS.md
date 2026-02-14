# IntegrateAgent Status

Date: February 14, 2026

## Implemented
- [x] Tray icon present and working (status_ok/status_bad icons)
- [x] Server start/stop via tray menu
- [x] `GET /health` endpoint
- [x] `POST /command` endpoint
- [x] Bearer auth via `AGENT_TOKEN`
- [x] Allowlist enforcement for `run_app`
- [x] Allowlist enforcement for `key_press`
- [x] `key_press` supports modifier combinations (modifiers held, non-modifier pressed, then modifiers released)
- [x] Rotating file logging to `%APPDATA%\IntegrateAgent\logs\agent.log`
- [x] Voicemeeter Potato integration (apply, group bus gain, command, get, set)
- [x] Voicemeeter allowlists for targets/fields/commands

## How to Run
Tray app:
```powershell
python -m tray.tray_app
```

No-console tray app:
```powershell
pythonw -m tray.tray_app
```

Server (manual):
```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8765
```

## How to Test
Health check:
```powershell
curl http://127.0.0.1:8765/health
```

Run app:
```powershell
curl -X POST http://127.0.0.1:8765/command ^
  -H "Authorization: Bearer your-token" ^
  -H "Content-Type: application/json" ^
  -d "{\"request_id\":\"1\",\"action\":\"run_app\",\"payload\":{\"app\":\"notepad\"}}"
```

Key press:
```powershell
curl -X POST http://127.0.0.1:8765/command ^
  -H "Authorization: Bearer your-token" ^
  -H "Content-Type: application/json" ^
  -d "{\"request_id\":\"2\",\"action\":\"key_press\",\"payload\":{\"keys\":[\"ctrl\",\"s\"]}}"
```

Voicemeeter apply:
```powershell
curl -X POST http://127.0.0.1:8765/command ^
  -H "Authorization: Bearer your-token" ^
  -H "Content-Type: application/json" ^
  -d "{\"request_id\":\"3\",\"action\":\"voicemeeter_apply\",\"payload\":{\"settings\":{\"strip-0\":{\"gain\":-6.0},\"bus-0\":{\"gain\":0.0}}}}"
```

Voicemeeter group bus gain:
```powershell
curl -X POST http://127.0.0.1:8765/command ^
  -H "Authorization: Bearer your-token" ^
  -H "Content-Type: application/json" ^
  -d "{\"request_id\":\"4\",\"action\":\"voicemeeter_group_bus_gain\",\"payload\":{\"gain\":-3.0}}"
```

Voicemeeter command:
```powershell
curl -X POST http://127.0.0.1:8765/command ^
  -H "Authorization: Bearer your-token" ^
  -H "Content-Type: application/json" ^
  -d "{\"request_id\":\"5\",\"action\":\"voicemeeter_command\",\"payload\":{\"command\":\"reset\"}}"
```

Voicemeeter get (targets/fields):
```powershell
curl -X POST http://127.0.0.1:8765/command ^
  -H "Authorization: Bearer your-token" ^
  -H "Content-Type: application/json" ^
  -d "{\"request_id\":\"6\",\"action\":\"voicemeeter_get\",\"payload\":{\"targets\":[\"strip-0\",\"strip-1\"],\"fields\":[\"gain\",\"mute\"]}}"
```

Voicemeeter set/get (raw params, requires allowlist):
```powershell
curl -X POST http://127.0.0.1:8765/command ^
  -H "Authorization: Bearer your-token" ^
  -H "Content-Type: application/json" ^
  -d "{\"request_id\":\"7\",\"action\":\"voicemeeter_set\",\"payload\":{\"params\":[{\"param\":\"Strip[0].Mute\",\"value\":true}]}}"
```

```powershell
curl -X POST http://127.0.0.1:8765/command ^
  -H "Authorization: Bearer your-token" ^
  -H "Content-Type: application/json" ^
  -d "{\"request_id\":\"8\",\"action\":\"voicemeeter_get\",\"payload\":{\"params\":[{\"param\":\"Strip[0].Mute\"}]}}"
```

PowerShell example:
```powershell
$body = @{ request_id = "9"; action = "key_press"; payload = @{ keys = @("ctrl","shift","s") } } | ConvertTo-Json -Depth 4
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8765/command" -Headers @{ Authorization = "Bearer your-token" } -Body $body -ContentType "application/json"
```

## Latest Test Run (February 14, 2026)
- [x] `/health` returned ok
- [x] `voicemeeter_get` for `strip-0` gain/mute
- [x] `voicemeeter_apply` set `strip-0` gain and read back
- [x] `voicemeeter_group_bus_gain` set bus 0-2 gain and read back
- [x] `voicemeeter_command` reset succeeded

## Known Limitations / TODO (Optional Polish Only)
- No UI to edit allowlists (requires manual changes in `server/config.py`).
- Tray app health polling interval is fixed (2 seconds).
- No TLS (intended for localhost only).
- Raw Voicemeeter param access is disabled unless allowlisted.
