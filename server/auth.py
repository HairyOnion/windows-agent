from __future__ import annotations

import os
from fastapi import Header, HTTPException


def get_token_or_raise() -> str:
    token = os.environ.get("AGENT_TOKEN")
    if not token:
        raise RuntimeError("AGENT_TOKEN is not set; refusing to start server.")
    return token


def verify_bearer(authorization: str | None = Header(default=None)) -> None:
    token = get_token_or_raise()
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    provided = authorization.split(" ", 1)[1].strip()
    if provided != token:
        raise HTTPException(status_code=403, detail="Invalid token")
