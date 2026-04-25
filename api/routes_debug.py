from fastapi import APIRouter
from api.runtime import get_runtime

router = APIRouter(prefix="/debug", tags=["debug"])

@router.post("/test-action")
def trigger_test_action():
    executor = get_runtime("executor")
    if executor is None:
        return {"ok": False, "error": "executor not registered"}
    return {
        "ok": True,
        "message": "executor registered",
        "last_render": getattr(executor, "last_render", {}),
    }

@router.get("/errors")
def list_errors():
    memory_manager = get_runtime("memory_manager")
    if memory_manager is None:
        return {"ok": False, "error": "memory_manager not registered"}

    rows = memory_manager.retrieval.get_recent_errors(limit=10)
    return {"ok": True, "items": rows}
