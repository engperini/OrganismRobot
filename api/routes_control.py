from fastapi import APIRouter
from api.server import get_runtime

router = APIRouter(prefix="/control", tags=["control"])

def _set_mode(mode: str):
    state_store = get_runtime("state_store")
    if state_store is None:
        return {"ok": False, "error": "state_store not registered"}

    state_store.update(mode=mode)
    return {"ok": True, "mode": mode}

@router.post("/idle")
def set_mode_idle():
    return _set_mode("idle")

@router.post("/explore")
def set_mode_explore():
    return _set_mode("explore")

@router.post("/safe-stop")
def set_mode_safe_stop():
    return _set_mode("safe_stop")
