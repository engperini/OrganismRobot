from fastapi import APIRouter
from api.runtime import get_runtime

router = APIRouter(prefix="/status", tags=["status"])

@router.get("/world")
def get_world_state():
    state_store = get_runtime("state_store")
    if state_store is None:
        return {"ok": False, "error": "state_store not registered"}
    return {"ok": True, "world_state": state_store.get().model_dump()}

@router.get("/sensors")
def get_sensor_snapshot():
    sensor_hub = get_runtime("sensor_hub")
    if sensor_hub is None:
        return {"ok": False, "error": "sensor_hub not registered"}
    snapshot = sensor_hub.get()
    return {"ok": True, "sensor_snapshot": snapshot.model_dump()}

@router.get("/last-thought")
def get_last_thought():
    last_thought = get_runtime("last_thought")
    if last_thought is None:
        return {"ok": True, "last_thought": None}
    return {"ok": True, "last_thought": last_thought.model_dump()}

@router.get("/last-plan")
def get_last_plan():
    last_plan = get_runtime("last_plan")
    if last_plan is None:
        return {"ok": True, "last_plan": None}
    return {"ok": True, "last_plan": last_plan.model_dump()}

@router.get("/last-result")
def get_last_result():
    last_result = get_runtime("last_result")
    if last_result is None:
        return {"ok": True, "last_result": None}
    return {"ok": True, "last_result": last_result.model_dump()}

@router.get("/last-episode")
def get_last_episode():
    last_reflection = get_runtime("last_reflection")
    if last_reflection is None:
        return {"ok": True, "last_episode": None}
    return {"ok": True, "last_episode": last_reflection.model_dump()}
