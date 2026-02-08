# IntegrateAgent Status

Date: February 7, 2026

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

PowerShell example:
```powershell
$body = @{ request_id = "3"; action = "key_press"; payload = @{ keys = @("ctrl","shift","s") } } | ConvertTo-Json -Depth 4
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8765/command" -Headers @{ Authorization = "Bearer your-token" } -Body $body -ContentType "application/json"
```

## Known Limitations / TODO (Optional Polish Only)
- No UI to edit allowlists (requires manual changes in `server/config.py`).
- Tray app health polling interval is fixed (2 seconds).
- No TLS (intended for localhost only).
