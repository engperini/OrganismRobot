from fastapi import APIRouter

router = APIRouter(prefix="/status", tags=["status"])

@router.get("/world")
def get_world_state():
    return {"status": "placeholder"}

@router.get("/sensors")
def get_sensor_snapshot():
    return {"status": "placeholder"}

@router.get("/last-thought")
def get_last_thought():
    return {"status": "placeholder"}

@router.get("/last-episode")
def get_last_episode():
    return {"status": "placeholder"}
