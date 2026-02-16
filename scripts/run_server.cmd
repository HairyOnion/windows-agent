@echo off
setlocal

cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
  echo Missing virtual environment. Run scripts\setup_windows.cmd first.
  exit /b 1
)

if not exist ".env" (
  echo Missing .env file. Create it from .env.example and set AGENT_TOKEN.
  exit /b 1
)

for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
  if /I "%%A"=="AGENT_TOKEN" set "AGENT_TOKEN=%%B"
)

if "%AGENT_TOKEN%"=="" (
  echo AGENT_TOKEN is not set in .env
  exit /b 1
)

".venv\Scripts\python.exe" -m uvicorn server.main:app --host 0.0.0.0 --port 8765
