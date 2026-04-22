from fastapi import APIRouter

router = APIRouter(prefix="/control", tags=["control"])

@router.post("/idle")
def set_mode_idle():
    return {"ok": True, "mode": "idle"}

@router.post("/explore")
def set_mode_explore():
    return {"ok": True, "mode": "explore"}

@router.post("/safe-stop")
def set_mode_safe_stop():
    return {"ok": True, "mode": "safe_stop"}
