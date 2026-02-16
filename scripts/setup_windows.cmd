@echo off
setlocal

cd /d "%~dp0.."

where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher 'py' was not found.
  echo Install Python 3.11+ from python.org or via winget, then rerun this script.
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Failed to create venv. Run: py -0p to list installed versions.
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo Failed to activate .venv
  exit /b 1
)

echo Installing project dependencies...
pip install -e .
if errorlevel 1 (
  echo Dependency install failed.
  exit /b 1
)

if not exist ".env" (
  copy /y ".env.example" ".env" >nul
  echo Created .env from .env.example
)

echo Setup complete.
echo Next: edit .env and set AGENT_TOKEN, then run scripts\run_tray.cmd

exit /b 0
