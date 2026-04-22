from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from api.server import get_runtime

router = APIRouter(prefix="/control", tags=["control"])


class ControlUpdate(BaseModel):
    mode: str
    current_goal: Optional[str] = None


def _set_state(mode: str, current_goal: Optional[str] = None):
    state_store = get_runtime("state_store")
    if state_store is None:
        return {"ok": False, "error": "state_store not registered"}

    update_payload = {"mode": mode}
    if current_goal is not None:
        update_payload["current_goal"] = current_goal

    state_store.update(**update_payload)
    return {
        "ok": True,
        "mode": mode,
        "current_goal": current_goal,
    }


@router.post("/idle")
def set_mode_idle():
    return _set_state("idle", "monitor safely")


@router.post("/explore")
def set_mode_explore():
    return _set_state("explore", "explore environment")


@router.post("/safe-stop")
def set_mode_safe_stop():
    return _set_state("safe_stop", "halt safely")


@router.post("/set")
def set_mode_and_goal(payload: ControlUpdate):
    return _set_state(payload.mode, payload.current_goal)
