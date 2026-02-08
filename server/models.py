from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    request_id: str = Field(..., min_length=1)
    action: Literal["run_app", "key_press"]
    payload: Dict[str, Any]


class CommandResponse(BaseModel):
    request_id: str
    ok: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class RunAppPayload(BaseModel):
    app: str
    args: Optional[List[str]] = None


class KeyPressPayload(BaseModel):
    keys: List[str]
