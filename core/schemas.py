from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class RawSensorSnapshot(BaseModel):
    ts: datetime = Field(default_factory=datetime.utcnow)
    distance_front_cm: Optional[float] = None
    servo_pan_deg: Optional[float] = None
    servo_tilt_deg: Optional[float] = None
    left_motor_state: str = "stop"
    right_motor_state: str = "stop"
    battery_pct: Optional[int] = None
    last_error: Optional[str] = None
    camera_summary: Optional[str] = None
    audio_summary: Optional[str] = None


class Event(BaseModel):
    ts: datetime = Field(default_factory=datetime.utcnow)
    source: str
    type: str
    data: Dict[str, Any]


class Perception(BaseModel):
    ts: datetime = Field(default_factory=datetime.utcnow)
    summary: str
    risk_flags: List[str] = []
    attention_candidates: List[str] = []
    novelty_hints: List[str] = []


class WorldState(BaseModel):
    ts: datetime = Field(default_factory=datetime.utcnow)
    mode: str = "booting"
    current_goal: str = "initialize"
    energy_mode: str = "normal"
    mood: str = "idle"
    attention_target: Optional[str] = None
    front_distance_cm: Optional[float] = None
    servo_pan_deg: Optional[float] = None
    servo_tilt_deg: Optional[float] = None
    motors_state: str = "stopped"
    battery_pct: Optional[int] = None
    risk_flags: List[str] = []
    last_action: Optional[str] = None
    last_error: Optional[str] = None


class Thought(BaseModel):
    assessment: str
    intent: str
    strategy: List[str]
    mood: Optional[str] = None
    store_candidate: bool = False
    why_store: Optional[str] = None


class PlanAction(BaseModel):
    tool: str
    args: Dict[str, Any] = {}
    timeout_s: float = 1.0


class ExecutablePlan(BaseModel):
    plan_id: str
    actions: List[PlanAction]
    policy: Dict[str, Any] = {}
    expression: Optional[Dict[str, Any]] = None
    voice_hint: Optional[str] = None
    store_memory: bool = False
    memory_hint: Optional[str] = None


class ExecutionResult(BaseModel):
    plan_id: str
    status: str
    completed_actions: int = 0
    failed_action: Optional[str] = None
    failure_reason: Optional[str] = None
    duration_s: float = 0.0


class Reflection(BaseModel):
    episode_summary: str
    lesson: Optional[str] = None
    store_structured: bool = False
    novelty_score: float = 0.0
    policy_feedback: Optional[Dict[str, Any]] = None


class ExpressionState(BaseModel):
    mood: str = "neutral"
    face_mode: str = "neutral"


class InnerVoiceMessage(BaseModel):
    text: str
    duration_s: float = 2.0
    priority: str = "normal"
