from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    request_id: str = Field(..., min_length=1)
    action: Literal[
        "run_app",
        "key_press",
        "voicemeeter_apply",
        "voicemeeter_group_bus_gain",
        "voicemeeter_command",
        "voicemeeter_get",
        "voicemeeter_set",
    ]
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


class VoicemeeterApplyPayload(BaseModel):
    settings: Dict[str, Dict[str, Any]]


class VoicemeeterGroupBusGainPayload(BaseModel):
    gain: float


class VoicemeeterCommandPayload(BaseModel):
    command: Literal["restart", "reset"]


class VoicemeeterParamGet(BaseModel):
    param: str
    is_string: Optional[bool] = False


class VoicemeeterGetPayload(BaseModel):
    targets: Optional[List[str]] = None
    fields: Optional[List[str]] = None
    params: Optional[List[VoicemeeterParamGet]] = None


class VoicemeeterParamSet(BaseModel):
    param: str
    value: Any


class VoicemeeterSetPayload(BaseModel):
    params: List[VoicemeeterParamSet]
