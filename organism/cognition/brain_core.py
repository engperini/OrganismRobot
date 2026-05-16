import os
import json
import random
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any


def clamp(v, low=0.0, high=1.0):
    try:
        return max(low, min(high, float(v)))
    except Exception:
        return low


def safe_json_loads(text, fallback):
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else fallback
    except Exception:
        return fallback


@dataclass
class RawWorld:
    cycle: int
    raw_scene: str
    changed: bool
    distance_front_cm: Optional[float]
    battery_pct: Optional[int]
    runtime_mode: str


@dataclass
class Perception:
    cycle: int
    raw_scene: str
    scene_summary: str
    entities: List[str]
    attention_candidates: List[str]
    novelty: float
    risk: float
    social_presence: bool
    uncertainty: float
    changed: bool
    distance_front_cm: Optional[float]
    runtime_mode: str


@dataclass
class FocusState:
    target: Optional[str] = None
    reason: Optional[str] = None
    interest: float = 0.0
    age_cycles: int = 0
    status: str = "none"

    def active(self):
        return self.target is not None and self.interest > 0.25


@dataclass
class GoalState:
    macro_goal: str = "understand the environment and seek meaning"
    micro_goal: str = "observe the environment"
    success_condition: str = "notice relevant change"
    age_cycles: int = 0


@dataclass
class Thought:
    assessment: str
    intent: str
    intent_type: str
    micro_goal: str
    success_condition: str
    mood: str
    attention_target: Optional[str]
    curiosity: float
    urgency: float
    confidence: float
    inner_voice: str


@dataclass
class Action:
    name: str
    target: Optional[str] = None
    direction: Optional[str] = None
    intensity: float = 0.5
    args: Dict[str, Any] = None


class LLM:
    def __init__(self):
        self.use_llm = os.getenv("USE_LLM", "true").lower() == "true"
        self.model = os.getenv("ORGANISM_MODEL", "gpt-4o-mini")
        self.client = None

        if self.use_llm:
            try:
                from openai import OpenAI
                self.client = OpenAI()
            except Exception as exc:
                print(f"[LLM] fallback mode: {exc}")
                self.use_llm = False

    def complete_json(self, system, prompt, fallback):
        print(">>> LLM:", "on=" + str(self.use_llm), "model=" + self.model)

        if not self.use_llm or self.client is None:
            return fallback

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=system,
                input=json.dumps(prompt, ensure_ascii=False),
            )
            text = response.output_text.strip()
            return safe_json_loads(text, fallback)
        except Exception as exc:
            print(f"[LLM] error, fallback: {exc}")
            return fallback


class BrainMemory:
    def __init__(self, max_items=50):
        self.items = []
        self.max_items = max_items

    def add(self, item):
        self.items.append(item)
        self.items = self.items[-self.max_items:]

    def recent(self, n=8):
        return self.items[-n:]

    def recent_affective_memory(self, n=10):
        out = []
        for item in self.recent(n):
            out.append({
                "cycle": item.get("cycle"),
                "focus_target": item.get("focus_target"),
                "intent_type": item.get("intent_type"),
                "action": item.get("action"),
                "novelty": item.get("novelty"),
                "progress": item.get("progress"),
                "risk": item.get("risk"),
                "reflection": item.get("reflection"),
                "focus_decision": item.get("focus_decision"),
            })
        return out

    def repeated_pattern(self):
        recent = self.recent(4)
        if len(recent) < 3:
            return False

        signatures = [
            f"{x.get('focus_target')}|{x.get('intent_type')}|{x.get('action')}"
            for x in recent[-3:]
        ]
        return len(set(signatures)) == 1


class PerceptionInterpreter:
    def __init__(self, llm):
        self.llm = llm

    def interpret(self, raw, memory):
        fallback = {
            "scene_summary": raw.raw_scene,
            "entities": ["visual scene"] if raw.raw_scene else ["limited perception"],
            "attention_candidates": ["visual scene"] if raw.raw_scene else ["limited perception"],
            "novelty": 0.45 if raw.changed else 0.20,
            "risk": 0.9 if raw.distance_front_cm is not None and raw.distance_front_cm < 20 else 0.2,
            "social_presence": False,
            "uncertainty": 0.4 if raw.raw_scene else 0.8,
        }

        system = (
            "You are the perception interpreter of an embodied artificial organism. "
            "Extract entities, attention candidates, novelty, risk and uncertainty from the raw scene. "
            "Use short concrete labels. Return valid JSON only."
        )

        prompt = {
            "raw_world": asdict(raw),
            "recent_memory": memory.recent(5),
            "required_json": {
                "scene_summary": "short scene summary",
                "entities": ["entity"],
                "attention_candidates": ["candidate"],
                "novelty": 0.0,
                "risk": 0.0,
                "social_presence": False,
                "uncertainty": 0.0,
            },
            "rules": [
                "Do not invent objects not present in raw_scene.",
                "If distance_front_cm is below 20, risk must be high.",
                "If raw_scene repeats, novelty should be lower.",
                "If the visual field is weak or ambiguous, uncertainty should increase.",
            ],
        }

        data = self.llm.complete_json(system, prompt, fallback)

        entities = data.get("entities") if isinstance(data.get("entities"), list) else fallback["entities"]
        candidates = data.get("attention_candidates") if isinstance(data.get("attention_candidates"), list) else entities[:1]

        return Perception(
            cycle=raw.cycle,
            raw_scene=raw.raw_scene,
            scene_summary=str(data.get("scene_summary", fallback["scene_summary"])),
            entities=entities or ["limited perception"],
            attention_candidates=candidates or ["limited perception"],
            novelty=clamp(data.get("novelty", fallback["novelty"])),
            risk=clamp(data.get("risk", fallback["risk"])),
            social_presence=bool(data.get("social_presence", fallback["social_presence"])),
            uncertainty=clamp(data.get("uncertainty", fallback["uncertainty"])),
            changed=raw.changed,
            distance_front_cm=raw.distance_front_cm,
            runtime_mode=raw.runtime_mode,
        )


class AttentionSystem:
    def __init__(self, llm):
        self.llm = llm

    def update(self, perception, focus, memory, state):
        fallback = self._fallback_attention(perception, focus, memory, state)

        system = (
            "You are the attention system of an embodied artificial organism. "
            "Decide whether to keep the current focus, change focus, or stay unfocused. "
            "Use perception, internal state and affective memory. Return valid JSON only."
        )

        prompt = {
            "perception": asdict(perception),
            "current_focus": asdict(focus),
            "internal_state": state.as_dict(),
            "recent_affective_memory": memory.recent_affective_memory(10),
            "repeated_pattern": memory.repeated_pattern(),
            "required_json": {
                "selected_focus": "target or null",
                "interest": 0.0,
                "status": "none | investigating | searching | shifting | avoiding",
                "reason": "short reason in first person",
            },
            "rules": [
                "If distance is unsafe, focus on safety.",
                "If repeated_pattern is true, prefer shifting attention.",
                "If a new candidate is more useful, choose it.",
                "Do not keep stale focus only because it existed before.",
            ],
        }

        data = self.llm.complete_json(system, prompt, fallback)

        selected = data.get("selected_focus", fallback["selected_focus"])
        if selected in ["null", "None", ""]:
            selected = None

        return FocusState(
            target=selected,
            reason=data.get("reason") or fallback["reason"],
            interest=clamp(data.get("interest", fallback["interest"])),
            age_cycles=(focus.age_cycles + 1 if selected and selected == focus.target else 0),
            status=data.get("status", fallback["status"]),
        )

    def _fallback_attention(self, perception, focus, memory, state):
        if perception.distance_front_cm is not None and perception.distance_front_cm < 20:
            return {
                "selected_focus": "front safety",
                "interest": 1.0,
                "status": "avoiding",
                "reason": "something is too close ahead",
            }

        if focus.active() and not memory.repeated_pattern() and state.boredom < 0.6:
            return {
                "selected_focus": focus.target,
                "interest": clamp(focus.interest + (0.05 if perception.changed else -0.1)),
                "status": "investigating",
                "reason": "the current focus still seems useful",
            }

        if perception.attention_candidates:
            return {
                "selected_focus": perception.attention_candidates[0],
                "interest": clamp(0.45 + perception.novelty - state.boredom * 0.2),
                "status": "investigating",
                "reason": "this candidate seems relevant now",
            }

        return {
            "selected_focus": None,
            "interest": 0.0,
            "status": "searching",
            "reason": "there is no clear focus",
        }


class Brain:
    def __init__(self, llm):
        self.llm = llm

    def think(self, perception, state, focus, goal, memory):
        fallback = {
            "assessment": f"I notice: {perception.scene_summary}",
            "intent": "I want to understand what matters here.",
            "intent_type": "observe" if focus.active() else "explore",
            "micro_goal": f"understand {focus.target}" if focus.active() else "find a useful focus",
            "success_condition": "notice progress, novelty or safety change",
            "mood": state.mood,
            "attention_target": focus.target,
            "curiosity": state.curiosity,
            "urgency": 0.2,
            "confidence": 0.5,
            "inner_voice": "Estou tentando entender o que importa.",
        }

        if perception.distance_front_cm is not None and perception.distance_front_cm < 20:
            fallback.update({
                "intent": "I need to stop because something is too close ahead.",
                "intent_type": "safe_stop",
                "micro_goal": "preserve safety",
                "mood": "alert",
                "urgency": 0.9,
                "inner_voice": "Tem algo perto demais. Vou parar.",
            })

        system = (
            "You are the inner cognitive self of an embodied artificial organism. "
            "Think in first person. You are not a chatbot. "
            "Form assessment, intention, micro-goal, mood and short inner voice. "
            "Return valid JSON only."
        )

        prompt = {
            "perception": asdict(perception),
            "internal_state": state.as_dict(),
            "focus": asdict(focus),
            "goal": asdict(goal),
            "recent_affective_memory": memory.recent_affective_memory(10),
            "repeated_pattern": memory.repeated_pattern(),
            "required_json": {
                "assessment": "short first-person assessment",
                "intent": "concrete first-person intention",
                "intent_type": "observe | explore | inspect_focus | approach_focus | avoid | safe_stop | wait | rest | interact | reorient",
                "micro_goal": "concrete micro-goal",
                "success_condition": "how I know I advanced",
                "mood": "curious | bored | cautious | calm | alert | tired | frustrated",
                "attention_target": "target or null",
                "curiosity": 0.0,
                "urgency": 0.0,
                "confidence": 0.0,
                "inner_voice": "short natural Portuguese phrase",
            },
            "rules": [
                "If distance_front_cm is below 20, choose safe_stop.",
                "If repeated_pattern is true and safe, change strategy.",
                "If bored and safe, seek novelty.",
                "Do not invent unavailable sensor data.",
                "inner_voice must be short and natural in Portuguese.",
            ],
        }

        data = self.llm.complete_json(system, prompt, fallback)

        attention_target = data.get("attention_target", fallback["attention_target"])
        if attention_target in ["null", "None", ""]:
            attention_target = None

        return Thought(
            assessment=str(data.get("assessment", fallback["assessment"])),
            intent=str(data.get("intent", fallback["intent"])),
            intent_type=str(data.get("intent_type", fallback["intent_type"])),
            micro_goal=str(data.get("micro_goal", fallback["micro_goal"])),
            success_condition=str(data.get("success_condition", fallback["success_condition"])),
            mood=str(data.get("mood", fallback["mood"])),
            attention_target=attention_target,
            curiosity=clamp(data.get("curiosity", fallback["curiosity"])),
            urgency=clamp(data.get("urgency", fallback["urgency"])),
            confidence=clamp(data.get("confidence", fallback["confidence"])),
            inner_voice=str(data.get("inner_voice", fallback["inner_voice"])),
        )

    def decide_action(self, thought, perception, focus, state, memory):
        fallback = self._fallback_action(thought, perception, focus, state, memory)

        system = (
            "You are the body executive of an embodied robot. "
            "Choose exactly one safe action. "
            "Use only available action names. Return valid JSON only."
        )

        prompt = {
            "thought": asdict(thought),
            "perception": asdict(perception),
            "focus": asdict(focus),
            "internal_state": state.as_dict(),
            "runtime_mode": perception.runtime_mode,
            "recent_affective_memory": memory.recent_affective_memory(8),
            "available_actions": [
                "motors.stop",
                "motors.forward",
                "motors.backward",
                "motors.turn_left",
                "motors.turn_right",
                "servos.center",
                "servos.random",
                "servos.look",
            ],
            "required_json": {
                "name": "action name",
                "target": "target or null",
                "direction": "left | right | front | back | null",
                "intensity": 0.0,
                "args": {},
            },
            "rules": [
                "If distance_front_cm is below 20, use motors.stop.",
                "In pc_simulation, do not move base; use servos only or motors.stop.",
                "In raspberry_hardware, explore may use short base movement if distance is safe.",
                "Use duration between 0.3 and 1.2 seconds for motors.",
                "Use servos.random for visual novelty without base movement.",
            ],
        }

        data = self.llm.complete_json(system, prompt, fallback)

        name = str(data.get("name", fallback["name"]))
        if name not in [
            "motors.stop",
            "motors.forward",
            "motors.backward",
            "motors.turn_left",
            "motors.turn_right",
            "servos.center",
            "servos.random",
            "servos.look",
        ]:
            name = fallback["name"]

        args = data.get("args", fallback.get("args", {}))
        if not isinstance(args, dict):
            args = {}

        if name.startswith("motors."):
            try:
                args["duration"] = max(0.3, min(float(args.get("duration", 0.7)), 1.2))
            except Exception:
                args["duration"] = 0.7

        if perception.runtime_mode == "pc_simulation" and name in [
            "motors.forward",
            "motors.backward",
            "motors.turn_left",
            "motors.turn_right",
        ]:
            name = "servos.random"
            args = {}

        if perception.distance_front_cm is not None and perception.distance_front_cm < 20:
            name = "motors.stop"
            args = {}

        return Action(
            name=name,
            target=data.get("target"),
            direction=data.get("direction"),
            intensity=clamp(data.get("intensity", fallback.get("intensity", 0.5))),
            args=args,
        )

    def _fallback_action(self, thought, perception, focus, state, memory):
        if perception.distance_front_cm is not None and perception.distance_front_cm < 20:
            return {"name": "motors.stop", "target": "front safety", "direction": None, "intensity": 1.0, "args": {}}

        if perception.runtime_mode == "pc_simulation":
            return {"name": "servos.random", "target": focus.target, "direction": None, "intensity": 0.5, "args": {}}

        if memory.repeated_pattern() and perception.distance_front_cm and perception.distance_front_cm > 30:
            return {"name": "motors.turn_left", "target": focus.target, "direction": "left", "intensity": 0.5, "args": {"duration": 0.7}}

        if thought.intent_type in ["explore", "reorient"] and perception.distance_front_cm and perception.distance_front_cm > 30:
            return {"name": "motors.turn_left", "target": focus.target, "direction": "left", "intensity": 0.5, "args": {"duration": 0.7}}

        return {"name": "servos.random", "target": focus.target, "direction": None, "intensity": 0.5, "args": {}}

    def reflect(self, perception, thought, action, action_result, focus, goal, memory):
        progress = 0.5
        novelty = 0.6 if action.name not in ["motors.stop", "servos.center"] else 0.2
        risk = perception.risk

        fallback = {
            "summary": f"I executed {action.name} and evaluated the result.",
            "keep_focus": focus.active() and novelty > 0.35 and not memory.repeated_pattern(),
            "focus_decision": "keep" if novelty > 0.45 else "soften",
            "lesson": None if novelty > 0.3 else "I need to change strategy.",
            "novelty_score": novelty,
            "repetition_detected": memory.repeated_pattern(),
            "store": novelty > 0.6 or memory.repeated_pattern(),
        }

        system = (
            "You are the internal reflection layer of an embodied artificial organism. "
            "Evaluate novelty, progress, repetition, saturation and future motivation. "
            "Return valid JSON only."
        )

        prompt = {
            "perception": asdict(perception),
            "thought": asdict(thought),
            "action": asdict(action),
            "action_result": action_result,
            "focus": asdict(focus),
            "goal": asdict(goal),
            "recent_affective_memory": memory.recent_affective_memory(10),
            "required_json": {
                "summary": "short first-person summary",
                "keep_focus": True,
                "focus_decision": "keep | soften | abandon | avoid_temporarily | return_later",
                "lesson": "useful lesson or null",
                "novelty_score": 0.0,
                "repetition_detected": False,
                "store": False,
            },
            "rules": [
                "Repetition means repeating focus, intention and action without real gain.",
                "If safe_stop happened because distance was low, do not treat that as boredom.",
                "If the scene repeated, suggest changing attention or perspective.",
                "Do not store generic lessons.",
            ],
        }

        data = self.llm.complete_json(system, prompt, fallback)

        return {
            "summary": str(data.get("summary", fallback["summary"])),
            "keep_focus": bool(data.get("keep_focus", fallback["keep_focus"])),
            "focus_decision": str(data.get("focus_decision", fallback["focus_decision"])),
            "lesson": data.get("lesson", fallback["lesson"]),
            "novelty_score": clamp(data.get("novelty_score", fallback["novelty_score"])),
            "repetition_detected": bool(data.get("repetition_detected", fallback["repetition_detected"])),
            "store": bool(data.get("store", fallback["store"])),
            "progress": progress,
            "risk": risk,
        }


class BrainCore:
    def __init__(self):
        print("[brain] Organic BrainCore initialized")
        self.llm = LLM()
        self.memory = BrainMemory()
        self.perception_interpreter = PerceptionInterpreter(self.llm)
        self.attention = AttentionSystem(self.llm)
        self.brain = Brain(self.llm)

        self.focus = FocusState()
        self.goal = GoalState()
        self.cycle = 0
        self.last_raw_scene = None
        self.last_perception = None
        self.last_thought = None
        self.last_action = None

    def _extract_scene(self, world):
        camera = world.get("camera_summary") or {}
        llm = camera.get("llm_description") or {}
        description = llm.get("description")
        if description:
            return description
        if world.get("adapter_error"):
            return "adapter error: " + str(world.get("adapter_error"))
        return "visual perception unavailable"

    def _raw_world_from_adapter(self, world):
        self.cycle += 1
        raw_scene = self._extract_scene(world)
        changed = raw_scene != self.last_raw_scene
        self.last_raw_scene = raw_scene

        return RawWorld(
            cycle=self.cycle,
            raw_scene=raw_scene,
            changed=changed,
            distance_front_cm=world.get("distance_front_cm"),
            battery_pct=world.get("battery_pct"),
            runtime_mode=world.get("runtime_mode", "unknown"),
        )

    def think(self, world, state, memory=None):
        raw = self._raw_world_from_adapter(world)

        perception = self.perception_interpreter.interpret(raw, self.memory)

        self.focus = self.attention.update(
            perception=perception,
            focus=self.focus,
            memory=self.memory,
            state=state,
        )

        if not self.focus.active():
            self.goal.micro_goal = "buscar um novo foco de atencao"
            self.goal.success_condition = "encontrar algo relevante"

        thought = self.brain.think(
            perception=perception,
            state=state,
            focus=self.focus,
            goal=self.goal,
            memory=self.memory,
        )

        action = self.brain.decide_action(
            thought=thought,
            perception=perception,
            focus=self.focus,
            state=state,
            memory=self.memory,
        )

        state.curiosity = thought.curiosity
        state.mood = thought.mood

        self.last_perception = perception
        self.last_thought = thought
        self.last_action = action

        return {
            "cycle": self.cycle,
            "intent": thought.intent,
            "intent_type": thought.intent_type,
            "micro_goal": thought.micro_goal,
            "success_condition": thought.success_condition,
            "mood": thought.mood,
            "inner_voice": thought.inner_voice,
            "attention_target": thought.attention_target,
            "focus": asdict(self.focus),
            "goal": asdict(self.goal),
            "perception": asdict(perception),
            "action": {
                "name": action.name,
                "args": action.args or {},
            },
            "runtime_mode": raw.runtime_mode,
            "state": state.as_dict(),
            "memory_size": len(self.memory.items),
            "repeated_pattern": self.memory.repeated_pattern(),
        }

    def reflect_after_action(self, action_result, state):
        if not self.last_perception or not self.last_thought or not self.last_action:
            return {"summary": "no cycle to reflect"}

        reflection = self.brain.reflect(
            perception=self.last_perception,
            thought=self.last_thought,
            action=self.last_action,
            action_result=action_result,
            focus=self.focus,
            goal=self.goal,
            memory=self.memory,
        )

        self._update_state(state, reflection)
        self._update_goal(reflection)
        self._update_focus(reflection)

        self.memory.add({
            "cycle": self.last_perception.cycle,
            "raw_scene": self.last_perception.raw_scene,
            "scene_summary": self.last_perception.scene_summary,
            "focus_target": self.focus.target,
            "macro_goal": self.goal.macro_goal,
            "micro_goal": self.last_thought.micro_goal,
            "intent_type": self.last_thought.intent_type,
            "action": self.last_action.name,
            "result": action_result,
            "novelty": reflection.get("novelty_score"),
            "progress": reflection.get("progress"),
            "risk": reflection.get("risk"),
            "reflection": reflection.get("summary"),
            "lesson": reflection.get("lesson"),
            "focus_decision": reflection.get("focus_decision"),
        })

        return reflection

    def _update_state(self, state, reflection):
        repeated = reflection.get("repetition_detected", False)
        novelty = reflection.get("novelty_score", 0.0)
        focus_decision = reflection.get("focus_decision")

        if repeated or novelty < 0.35 or focus_decision in ["abandon", "avoid_temporarily", "return_later"]:
            state.boredom = clamp(getattr(state, "boredom", 0.0) + 0.10)
            state.curiosity = clamp(getattr(state, "curiosity", 0.5) - 0.04)
        else:
            state.boredom = clamp(getattr(state, "boredom", 0.0) - 0.05)
            state.curiosity = clamp(getattr(state, "curiosity", 0.5) + 0.04)

        state.energy = clamp(getattr(state, "energy", 1.0) - 0.02)

        if state.energy < 0.25:
            state.mood = "tired"
        elif state.boredom > 0.65:
            state.mood = "bored"

    def _update_goal(self, reflection):
        self.goal.age_cycles += 1
        if reflection.get("focus_decision") in ["abandon", "avoid_temporarily", "return_later"]:
            self.goal.micro_goal = "buscar novo foco de atencao"
            self.goal.success_condition = "perceber mudanca relevante"

    def _update_focus(self, reflection):
        if not self.focus.active():
            return

        decision = reflection.get("focus_decision")

        if decision == "keep" and reflection.get("keep_focus"):
            self.focus.interest = clamp(self.focus.interest + 0.05)
        elif decision == "soften":
            self.focus.interest = clamp(self.focus.interest - 0.20)
        elif decision in ["abandon", "avoid_temporarily", "return_later"]:
            self.focus.interest = clamp(self.focus.interest - 0.45)
        else:
            self.focus.interest = clamp(self.focus.interest - 0.10)

        if self.focus.interest <= 0.25:
            self.focus = FocusState()
