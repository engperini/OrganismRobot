from fastapi import APIRouter

router = APIRouter(prefix="/debug", tags=["debug"])

@router.post("/test-action")
def trigger_test_action():
    return {"ok": True, "message": "test action placeholder"}

@router.get("/errors")
def list_errors():
    return {"items": []}
