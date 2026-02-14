from __future__ import annotations

import datetime as dt
import logging
import time
from typing import Any, Dict

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from .auth import get_token_or_raise, verify_bearer
from .executor import run_allowed_app
from .keypress import send_keys, validate_keys
from .logging_conf import setup_logging
from .models import (
    CommandRequest,
    CommandResponse,
    KeyPressPayload,
    RunAppPayload,
    VoicemeeterApplyPayload,
    VoicemeeterCommandPayload,
    VoicemeeterGetPayload,
    VoicemeeterGroupBusGainPayload,
    VoicemeeterSetPayload,
)
from .config import DEFAULT_HOST, DEFAULT_PORT, VERSION
from . import voicemeeter


app = FastAPI()
START_TIME = time.time()
LAST_REQUEST_UTC: str | None = None


def _now_utc() -> str:
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()


@app.on_event("startup")
def on_startup() -> None:
    get_token_or_raise()
    log_path = setup_logging()
    logging.getLogger("agent").info(
        "server_start",
        extra={
            "extra": {
                "event": "startup",
                "timestamp_utc": _now_utc(),
                "log_path": str(log_path),
                "host": DEFAULT_HOST,
                "port": DEFAULT_PORT,
                "version": VERSION,
            }
        },
    )


@app.on_event("shutdown")
def on_shutdown() -> None:
    voicemeeter.shutdown_vm()
    logging.getLogger("agent").info(
        "server_stop",
        extra={"extra": {"event": "shutdown", "timestamp_utc": _now_utc()}},
    )


@app.middleware("http")
async def track_last_request(request: Request, call_next):
    global LAST_REQUEST_UTC
    LAST_REQUEST_UTC = _now_utc()
    response = await call_next(request)
    return response


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "ok": True,
        "status": "running",
        "uptime_seconds": int(time.time() - START_TIME),
        "last_request_utc": LAST_REQUEST_UTC,
        "version": VERSION,
    }


@app.post("/command")
def command(
    req: CommandRequest,
    request: Request,
    _auth: None = Depends(verify_bearer),
) -> JSONResponse:
    logger = logging.getLogger("agent")
    caller_ip = request.client.host if request.client else "unknown"
    try:
        if req.action == "run_app":
            payload = RunAppPayload(**req.payload)
            proc = run_allowed_app(payload.app, payload.args or [])
            result = {"pid": proc.pid}
        elif req.action == "key_press":
            payload = KeyPressPayload(**req.payload)
            validate_keys(payload.keys)
            send_keys(payload.keys)
            result = {"sent": payload.keys}
        elif req.action == "voicemeeter_apply":
            payload = VoicemeeterApplyPayload(**req.payload)
            applied = voicemeeter.apply_settings(payload.settings)
            result = {"applied": applied}
        elif req.action == "voicemeeter_group_bus_gain":
            payload = VoicemeeterGroupBusGainPayload(**req.payload)
            result = voicemeeter.apply_group_bus_gain(payload.gain)
        elif req.action == "voicemeeter_command":
            payload = VoicemeeterCommandPayload(**req.payload)
            voicemeeter.run_command(payload.command)
            result = {"command": payload.command}
        elif req.action == "voicemeeter_get":
            payload = VoicemeeterGetPayload(**req.payload)
            if payload.params is not None:
                params = [param.dict() for param in payload.params]
                values = voicemeeter.get_params(params)
            else:
                targets = payload.targets or []
                fields = payload.fields or []
                values = voicemeeter.get_targets_fields(targets, fields)
            result = {"values": values}
        elif req.action == "voicemeeter_set":
            payload = VoicemeeterSetPayload(**req.payload)
            params = [param.dict() for param in payload.params]
            count = voicemeeter.set_params(params)
            result = {"applied": count}
        else:
            raise ValueError("Unknown action")

        logger.info(
            "command_ok",
            extra={
                "extra": {
                    "request_id": req.request_id,
                    "action": req.action,
                    "ok": True,
                    "error": None,
                    "caller_ip": caller_ip,
                    "timestamp_utc": _now_utc(),
                }
            },
        )
        return JSONResponse(CommandResponse(request_id=req.request_id, ok=True, result=result).dict())
    except Exception as exc:
        logger.error(
            "command_error",
            extra={
                "extra": {
                    "request_id": req.request_id,
                    "action": req.action,
                    "ok": False,
                    "error": str(exc),
                    "caller_ip": caller_ip,
                    "timestamp_utc": _now_utc(),
                }
            },
        )
        return JSONResponse(
            CommandResponse(request_id=req.request_id, ok=False, error=str(exc)).dict(),
            status_code=400,
        )
