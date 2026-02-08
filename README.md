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

## Notes
- Server binds to 127.0.0.1:8765 by default.
- Authorization is required for `/command`.
- App allowlist and key allowlist are in `server/config.py`.
- Logs are stored in `%APPDATA%\\IntegrateAgent\\logs\\agent.log`.
