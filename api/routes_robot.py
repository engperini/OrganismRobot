# routes_robot.py
from fastapi import APIRouter
from hardware_executor import execute_action

router = APIRouter()

@router.post("/robot/action")
def robot_action(action: str, duration: float = None, x: float = 0.0, y: float = 0.0):
    params = {"x": x, "y": y}
    if duration is not None:
        params["duration"] = duration
    execute_action(action, params)
    return {"status": "ok", "action": action}
