# routes_robot.py
from fastapi import APIRouter
from hardware_executor import execute_action

router = APIRouter()

@router.post("/robot/action")
def robot_action(action: str, x: float = 0.0, y: float = 0.0):
    execute_action(action, {"x": x, "y": y})
    return {"status": "ok", "action": action}
