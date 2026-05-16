import os
import json
import time
import random
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


# ============================================================
# MINI ORGANISM V2 - Generic Cognitive Loop
#
# Objetivo:
# - cérebro genérico
# - sem regra específica de pessoa/objeto/mesa
# - LLM decide interpretação, atenção, intenção, ação e reflexão
# - Python mantém apenas loop, estado, memória e simulação
# ============================================================


# ============================================================
# SCHEMAS
# ============================================================

@dataclass
class RawWorld:
    cycle: int
    raw_scene: str
    changed: bool


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


@dataclass
class InternalState:
    curiosity: float = 0.6
    boredom: float = 0.2
    energy: float = 0.8
    caution: float = 0.3
    frustration: float = 0.0
    mood: str = "curious"


@dataclass
class FocusState:
    target: Optional[str] = None
    reason: Optional[str] = None
    interest: float = 0.0
    age_cycles: int = 0
    status: str = "none"

    def active(self) -> bool:
        return self.target is not None and self.interest > 0.25


@dataclass
class GoalState:
    macro_goal: str = "entender o ambiente e buscar significado"
    micro_goal: str = "observar o ambiente"
    success_condition: str = "perceber algo relevante"
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


@dataclass
class ActionResult:
    action: Action
    outcome: str
    progress: float
    novelty: float
    risk: float


@dataclass
class Reflection:
    summary: str
    keep_focus: bool
    focus_decision: str
    avoid_target: Optional[str]
    avoid_reason: Optional[str]
    return_condition: Optional[str]
    next_attention_bias: Optional[str]
    change_macro_goal: Optional[str]
    lesson: Optional[str]
    novelty_score: float
    repetition_detected: bool
    store: bool


# ============================================================
# UTILS
# ============================================================

def clamp(v: float, low: float = 0.0, high: float = 1.0) -> float:
    try:
        return max(low, min(high, float(v)))
    except Exception:
        return low


def safe_json_loads(text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else fallback
    except Exception:
        return fallback


def print_box(title: str, content: str):
    print("\n" + "=" * 70)
    print(title)
    print("-" * 70)
    print(content)
    print("=" * 70)


# ============================================================
# LLM CLIENT
# ============================================================

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
                print(f"[LLM] Falha ao iniciar OpenAI. Usando fallback. Erro: {exc}")
                self.use_llm = False

    def complete_json(self, system: str, prompt: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
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
            print(f"[LLM] Erro. Usando fallback. {exc}")
            return fallback


# ============================================================
# WORLD SIMULATOR - genérico
# ============================================================

class WorldSimulator:
    def __init__(self):
        self.cycle = 0
        self.last_scene = None

        self.raw_scenes = [
            "Há uma forma pequena e colorida em uma região lateral, com fundo simples.",
            "A cena parece plana, repetitiva e com poucos detalhes perceptíveis.",
            "Há uma presença animada ou social parcialmente visível em uma região do campo visual.",
            "Existe um elemento distante próximo a uma região que pode exigir cautela.",
            "A percepção está pobre, com baixa textura e pouca mudança aparente.",
            "A cena contém múltiplas formas e possíveis detalhes novos, mas ainda incertos.",
            "Existe uma área com contraste visual que pode merecer inspeção.",
        ]

    def observe_raw(self) -> RawWorld:
        self.cycle += 1

        if self.cycle <= 2:
            raw_scene = self.raw_scenes[0]
        else:
            raw_scene = random.choice(self.raw_scenes)

        changed = raw_scene != self.last_scene
        self.last_scene = raw_scene

        return RawWorld(
            cycle=self.cycle,
            raw_scene=raw_scene,
            changed=changed,
        )

    def apply(self, action: Action, focus: FocusState) -> ActionResult:
        progress = random.uniform(0.1, 0.8)
        novelty = random.uniform(0.1, 0.7)
        risk = random.uniform(0.0, 0.4)

        if focus.active() and action.target == focus.target:
            progress += 0.15
            novelty += 0.05

        if action.name in ["wait", "rest"]:
            progress -= 0.15
            novelty -= 0.15

        if action.name in ["avoid", "retreat"]:
            risk -= 0.15
            progress += 0.05

        result = ActionResult(
            action=action,
            outcome=f"executei {action.name}"
                    + (f" em direção a {action.direction}" if action.direction else "")
                    + (f" com foco em {action.target}" if action.target else ""),
            progress=clamp(progress),
            novelty=clamp(novelty),
            risk=clamp(risk),
        )

        return result


# ============================================================
# MEMORY
# ============================================================

class Memory:
    def __init__(self, max_items: int = 40):
        self.items: List[Dict[str, Any]] = []
        self.max_items = max_items

    def add(self, item: Dict[str, Any]):
        self.items.append(item)
        self.items = self.items[-self.max_items:]

    def recent(self, n: int = 8) -> List[Dict[str, Any]]:
        return self.items[-n:]

    def recent_affective_memory(self, n: int = 10) -> List[Dict[str, Any]]:
        out = []
        for item in self.recent(n):
            out.append({
                "cycle": item.get("cycle"),
                "focus_target": item.get("focus_target"),
                "intent_type": item.get("intent_type"),
                "action": item.get("action"),
                "novelty": item.get("novelty"),
                "progress": item.get("progress"),
                "focus_decision": item.get("focus_decision"),
                "avoid_target": item.get("avoid_target"),
                "avoid_reason": item.get("avoid_reason"),
                "return_condition": item.get("return_condition"),
                "next_attention_bias": item.get("next_attention_bias"),
                "lesson": item.get("lesson"),
            })
        return out

    def repeated_pattern(self) -> bool:
        recent = self.recent(4)
        if len(recent) < 3:
            return False

        signatures = [
            f"{x.get('focus_target')}|{x.get('intent_type')}|{x.get('action')}"
            for x in recent[-3:]
        ]
        return len(set(signatures)) == 1


# ============================================================
# PERCEPTION INTERPRETER - LLM
# ============================================================

class PerceptionInterpreter:
    def __init__(self, llm: LLM):
        self.llm = llm

    def _fallback_perception(self, raw: RawWorld) -> Dict[str, Any]:
        text = raw.raw_scene.lower()

        if "presença" in text or "social" in text or "animada" in text:
            entity = "presença parcial"
        elif "elemento" in text or "distante" in text:
            entity = "elemento distante"
        elif "forma" in text:
            entity = "forma perceptível"
        elif "contraste" in text:
            entity = "região de contraste"
        elif "detalhe" in text or "múltiplas" in text:
            entity = "detalhe incerto"
        elif "pobre" in text or "baixa textura" in text:
            entity = "região pouco informativa"
        else:
            entity = "aspecto perceptivo incerto"

        return {
            "scene_summary": raw.raw_scene,
            "entities": [entity],
            "attention_candidates": [entity],
            "novelty": 0.45 if raw.changed else 0.25,
            "risk": 0.25,
            "social_presence": "presença" in text or "social" in text or "animada" in text,
            "uncertainty": 0.6,
        }
    
    def interpret(self, raw: RawWorld, memory: Memory) -> Perception:
        fallback = self._fallback_perception(raw)

        system = (
                "Você é um interpretador perceptivo genérico de um organismo artificial. "
                "Sua tarefa é extrair entidades perceptivas e candidatos de atenção da cena bruta. "
                "Nunca devolva entities vazio se houver qualquer coisa perceptível na raw_scene. "
                "Nunca devolva attention_candidates vazio se houver qualquer entidade. "
                "Use nomes curtos, concretos e genéricos. "
                "Não repita sempre o mesmo rótulo. "
                "Responda somente JSON válido."
                    )

        prompt = {
            "raw_world": asdict(raw),
            "recent_memory": memory.recent(5),
            "required_json": {
                "scene_summary": "resumo curto da cena",
                "entities": ["entidade abstrata 1", "entidade abstrata 2"],
                "attention_candidates": ["candidato de atenção"],
                "novelty": 0.0,
                "risk": 0.0,
                "social_presence": False,
                "uncertainty": 0.0,
            },
            "rules": [
                "Extraia entidades diretamente da raw_scene.",
                "Se a raw_scene mencionar forma, presença, elemento, contraste, detalhe, região, textura, mudança, distância ou cautela, gere entidades.",
                "attention_candidates devem ser escolhidos entre entities.",
                "Não use rótulos repetitivos como 'forma perceptível' em toda cena.",
                "Prefira rótulos variados e semânticos.",
                "Não retorne entities vazio quando houver algo percebido.",
                "Não retorne attention_candidates vazio quando houver entities.",
                "Se a cena for pobre, gere uma entidade como 'campo visual pobre' ou 'região pouco informativa'.",
                "novelty deve considerar changed e riqueza perceptiva.",
                "risk deve considerar cautela, distância, incerteza e possível presença social.",
                "uncertainty deve aumentar se a cena for ambígua, parcial ou pobre.",
            ],
        }

        data = self.llm.complete_json(system, prompt, fallback)

        if not data.get("entities"):
            data["entities"] = ["percepção indefinida"]

        if not data.get("attention_candidates"):
            data["attention_candidates"] = data["entities"][:1]

        return Perception(
            cycle=raw.cycle,
            raw_scene=raw.raw_scene,
            scene_summary=str(data.get("scene_summary", fallback["scene_summary"])),
            entities=data.get("entities") if isinstance(data.get("entities"), list) else [],
            attention_candidates=data.get("attention_candidates") if isinstance(data.get("attention_candidates"), list) else [],
            novelty=clamp(data.get("novelty", fallback["novelty"])),
            risk=clamp(data.get("risk", fallback["risk"])),
            social_presence=bool(data.get("social_presence", fallback["social_presence"])),
            uncertainty=clamp(data.get("uncertainty", fallback["uncertainty"])),
            changed=raw.changed,
        )


# ============================================================
# ATTENTION EVALUATOR - LLM
# ============================================================

class AttentionSystem:
    def __init__(self, llm: LLM):
        self.llm = llm

    def update(
        self,
        perception: Perception,
        focus: FocusState,
        memory: Memory,
        state: InternalState,
    ) -> FocusState:
        fallback = self._fallback_attention(perception, focus, memory, state)

        system = (
            "Você é o sistema de atenção de um organismo artificial genérico. "
            "Sua função é decidir se mantenho o foco atual, se mudo de foco, ou se fico sem foco. "
            "Não use regras específicas de objetos, pessoas, mesa, cor ou tipo. "
            "Use julgamento semântico e memória afetiva. "
            "Responda somente JSON válido."
        )

        prompt = {
            "perception": asdict(perception),
            "current_focus": asdict(focus),
            "internal_state": asdict(state),
            "recent_memory": memory.recent(8),
            "recent_affective_memory": memory.recent_affective_memory(10),
            "required_json": {
                "selected_focus": "alvo escolhido ou null",
                "keep_previous_focus": True,
                "is_focus_still_relevant": True,
                "interest": 0.0,
                "status": "none | investigating | searching | avoiding_recent_focus | shifting",
                "reason": "motivo curto em primeira pessoa",
            },
            "rules": [
              
            
               "Quando perception.changed=true, reavalie seriamente o foco atual.",
                "Se surgir attention_candidate semanticamente diferente do foco atual, considere trocar de foco.",
                "Não mantenha foco antigo apenas porque ele tinha interesse alto antes.",
                "Se social_presence=true e o foco atual não é social, considere redirecionar atenção.",
                "Se o novo candidato parecer mais relevante emocionalmente, escolha ele.",

                "Se perception.attention_candidates tiver candidato novo e perception.changed=true, compare com o foco atual.",
                "Se o candidato novo parecer mais útil, escolha o novo candidato.",
                "Não mantenha foco antigo só porque ainda há interesse.",
                "selected_focus deve ser o candidato mais útil agora, não necessariamente o anterior.",
               
                "Se o foco atual parece saturado, ignorado, repetitivo ou rejeitado na memória, devo mudar.",
                "Se não há candidato bom, selected_focus deve ser null.",
                "Não volte para avoid_target sem mudança real ou razão forte.",
                "interest deve ser coerente com novidade, tédio, risco e memória.",
                "Não use cooldown numérico.",
            ],
        }

        data = self.llm.complete_json(system, prompt, fallback)

        selected = data.get("selected_focus", None)
        if selected in ["null", "None", ""]:
            selected = None

        return FocusState(
            target=selected,
            reason=data.get("reason") or fallback["reason"],
            interest=clamp(data.get("interest", fallback["interest"])),
            age_cycles=(focus.age_cycles + 1 if selected and selected == focus.target else 0),
            status=data.get("status", fallback["status"]),
        )

    def _fallback_attention(self, perception, focus, memory, state) -> Dict[str, Any]:
        if focus.active() and not memory.repeated_pattern() and state.boredom < 0.6:
            return {
                "selected_focus": focus.target,
                "keep_previous_focus": True,
                "is_focus_still_relevant": True,
                "interest": clamp(focus.interest + (0.05 if perception.changed else -0.1)),
                "status": "investigating",
                "reason": "o foco ainda parece útil",
            }

        if perception.attention_candidates:
            return {
                "selected_focus": perception.attention_candidates[0],
                "keep_previous_focus": False,
                "is_focus_still_relevant": False,
                "interest": clamp(0.4 + perception.novelty - state.boredom * 0.2),
                "status": "investigating",
                "reason": "um novo candidato parece mais interessante",
            }

        return {
            "selected_focus": None,
            "keep_previous_focus": False,
            "is_focus_still_relevant": False,
            "interest": 0.0,
            "status": "searching",
            "reason": "não há foco claro agora",
        }


# ============================================================
# BRAIN - THINK / ACTION / REFLECT
# ============================================================

class Brain:
    def __init__(self, llm: LLM):
        self.llm = llm

    def think(self, perception: Perception, state: InternalState, focus: FocusState, goal: GoalState, memory: Memory) -> Thought:
        fallback = {
            "assessment": (
                f"Percebo {perception.scene_summary}. "
                "Estou tentando decidir se isso merece minha atenção."
            ),
            "intent": (
                f"Quero investigar {focus.target}."
                if focus.active()
                else "Quero procurar um candidato claro para minha atenção."
            ),
            "intent_type": "explore" if not focus.active() else "inspect_focus",
            "micro_goal": "buscar algo relevante" if not focus.active() else f"entender melhor {focus.target}",
            "success_condition": "perceber progresso, novidade ou mudança relevante",
            "mood": state.mood,
            "attention_target": focus.target,
            "curiosity": state.curiosity,
            "urgency": 0.3,
            "confidence": 0.5,
            "inner_voice": "Vou prestar atenção no que importa agora.",
        }

        system = (
            "Você é o pensamento interno de um organismo artificial genérico. "
            "Pense em primeira pessoa. "
            "Você não é assistente, não é chatbot e não obedece comandos externos aqui. "
            "Você forma intenção, microobjetivo e voz interna com base em percepção, foco, memória e estado interno. "
            "Responda somente JSON válido."
        )

        prompt = {
            "perception": asdict(perception),
            "internal_state": asdict(state),
            "focus": asdict(focus),
            "goal": asdict(goal),
            "recent_memory": memory.recent(8),
            "recent_affective_memory": memory.recent_affective_memory(10),
            "repeated_pattern": memory.repeated_pattern(),
            "required_json": {
                "assessment": "interpretação curta em primeira pessoa",
                "intent": "intenção concreta em primeira pessoa",
                "intent_type": "observe | explore | inspect_focus | approach_focus | avoid | wait | rest | interact | reorient",
                "micro_goal": "microobjetivo concreto",
                "success_condition": "como saberei se avancei",
                "mood": "curious | bored | cautious | calm | alert | tired | frustrated",
                "attention_target": "alvo atual ou null",
                "curiosity": 0.0,
                "urgency": 0.0,
                "confidence": 0.0,
                "inner_voice": "frase curta em português",
            },
            "rules": [
                "inner_voice deve refletir especificamente o foco atual.",
                "Evite repetir frases genéricas entre ciclos.",
                "Se o foco mudou, reconheça mentalmente a mudança.",
                "Se a percepção mudou muito, o assessment também deve mudar.",
                "Não use frases neutras como 'vou prestar atenção no que importa agora'.",
                "Evite: 'Vou prestar atenção no que importa agora'.",
                "Prefira frases como: 'Isso me chamou atenção.' ou 'Quero entender melhor esse foco.'",
                "Evite frases genéricas como 'formar uma intenção simples e coerente'.",
                "Se existir attention_candidate, use esse candidato como alvo mental.",
                "Se existir foco ativo, pense sobre ele de forma específica.",
                "inner_voice deve parecer pensamento vivo, não relatório técnico.",
                "Não reinicie a mente do zero.",
                "Use memória afetiva para não insistir no que foi rejeitado.",
                "Se boredom está alto, reconheça saturação e mude estratégia.",
                "Se há foco ativo, só continue se ainda fizer sentido.",
                "Se não há foco, procure formar um novo ou reorientar.",
                "Não use nomes específicos fixos; use o alvo que veio da percepção/atenção.",
                "A voz interna deve ser curta e natural.",
            ],
        }

        data = self.llm.complete_json(system, prompt, fallback)
                

        # ============================================================
        # coerência cognitiva mínima
        # ============================================================

        if focus.active():
            data["attention_target"] = focus.target

            if (
                not data.get("micro_goal")
                or "algo relevante" in str(data.get("micro_goal")).lower()
            ):
                data["micro_goal"] = f"entender melhor {focus.target}"

            if (
                not data.get("inner_voice")
                or "importa agora" in str(data.get("inner_voice")).lower()
            ):
                data["inner_voice"] = f"Quero entender melhor {focus.target}."

        else:
            data["attention_target"] = None

            if data.get("intent_type") in [
                "inspect_focus",
                "approach_focus",
            ]:
                data["intent_type"] = "explore"

            if "forma perceptível" in str(data.get("intent", "")).lower():
                data["intent"] = "Quero procurar um novo foco de atenção."
                data["micro_goal"] = "buscar um novo foco de atenção"

        attention_target = data.get(
            "attention_target",
            fallback["attention_target"]
        )

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

    def decide_action(self, thought: Thought, perception: Perception, focus: FocusState, state: InternalState, memory: Memory) -> Action:
        fallback = {
            "name": "inspect_focus" if focus.active() and thought.intent_type == "inspect_focus" else random.choice(["look_left", "look_right", "look_forward", "wait"]),
            "target": focus.target if focus.active() and thought.intent_type == "inspect_focus" else None,
            "direction": random.choice(["esquerda", "direita", "frente"]),
            "intensity": 0.5,
        }

        system = (
            "Você é o executivo corporal simulado de um organismo artificial genérico. "
            "Escolha uma única ação simples. "
            "Não use regras específicas de objetos. "
            "Responda somente JSON válido."
        )

        prompt = {
            "thought": asdict(thought),
            "perception": asdict(perception),
            "focus": asdict(focus),
            "internal_state": asdict(state),
            "recent_memory": memory.recent(6),
            "available_actions": [
                "look_left",
                "look_right",
                "look_forward",
                "inspect_focus",
                "approach_focus",
                "move_forward",
                "move_backward",
                "avoid",
                "wait",
                "rest",
                "interact",
                "reorient",
            ],
            "required_json": {
                "name": "nome da ação",
                "target": "alvo ou null",
                "direction": "esquerda | direita | frente | trás | null",
                "intensity": 0.0,
            },
            "rules": [
                "A ação deve servir ao microobjetivo.",
                "Se não há foco, não use inspect_focus.",
                "Se há risco ou cautela alta, prefira ação conservadora.",
                "Se está entediado, pode reorientar ou mudar direção.",
                "Escolha só uma ação.",
            ],
        }

        data = self.llm.complete_json(system, prompt, fallback)

        target = data.get("target", fallback["target"])
        if target in ["null", "None", ""]:
            target = None

        direction = data.get("direction", fallback["direction"])
        if direction in ["null", "None", ""]:
            direction = None

        return Action(
            name=str(data.get("name", fallback["name"])),
            target=target,
            direction=direction,
            intensity=clamp(data.get("intensity", fallback["intensity"])),
        )

    def reflect(
        self,
        perception: Perception,
        thought: Thought,
        action: Action,
        result: ActionResult,
        focus: FocusState,
        goal: GoalState,
        memory: Memory,
    ) -> Reflection:
        fallback = {
            "summary": f"Eu executei {action.name} e avaliei o resultado.",
            "keep_focus": focus.active() and result.novelty > 0.35 and not memory.repeated_pattern(),
            "focus_decision": "keep" if result.novelty > 0.45 else "soften",
            "avoid_target": None,
            "avoid_reason": None,
            "return_condition": None,
            "next_attention_bias": None,
            "change_macro_goal": None,
            "lesson": None if result.novelty > 0.3 else "Preciso mudar a estratégia.",
            "novelty_score": result.novelty,
            "repetition_detected": memory.repeated_pattern(),
            "store": result.novelty > 0.6 or memory.repeated_pattern(),
        }

        system = (
            "Você é a reflexão interna de um organismo artificial genérico. "
            "Avalie novidade, progresso, repetição, saturação, foco e motivação futura. "
            "Você pode decidir manter, suavizar, abandonar, evitar temporariamente ou voltar depois para um foco. "
            "Não use cooldown numérico. Use julgamento subjetivo e condição de retorno. "
            "Responda somente JSON válido."
        )

        prompt = {
            "perception": asdict(perception),
            "thought": asdict(thought),
            "action": asdict(action),
            "result": asdict(result),
            "focus": asdict(focus),
            "goal": asdict(goal),
            "recent_memory": memory.recent(8),
            "recent_affective_memory": memory.recent_affective_memory(10),
            "required_json": {
                "summary": "resumo curto em primeira pessoa",
                "keep_focus": True,
                "focus_decision": "keep | soften | abandon | avoid_temporarily | return_later",
                "avoid_target": "alvo a evitar ou null",
                "avoid_reason": "motivo subjetivo ou null",
                "return_condition": "quando aceito voltar ou null",
                "next_attention_bias": "tendência para próxima atenção ou null",
                "change_macro_goal": "novo macroobjetivo ou null",
                "lesson": "lição útil ou null",
                "novelty_score": 0.0,
                "repetition_detected": False,
                "store": False,
            },
            "rules": [
                "Repetição não é só repetir ação; é repetir foco/intenção/ação sem ganho real.",
                "Se o foco saturou, posso evitar temporariamente.",
                "Se o resultado trouxe novidade real, posso manter.",
                "Se estou sem foco, posso sugerir viés de atenção.",
                "Evite decisões mecânicas.",
            ],
        }

        data = self.llm.complete_json(system, prompt, fallback)

        avoid_target = data.get("avoid_target", fallback["avoid_target"])
        if avoid_target in ["null", "None", ""]:
            avoid_target = None

        return Reflection(
            summary=str(data.get("summary", fallback["summary"])),
            keep_focus=bool(data.get("keep_focus", fallback["keep_focus"])),
            focus_decision=str(data.get("focus_decision", fallback["focus_decision"])),
            avoid_target=avoid_target,
            avoid_reason=data.get("avoid_reason", fallback["avoid_reason"]),
            return_condition=data.get("return_condition", fallback["return_condition"]),
            next_attention_bias=data.get("next_attention_bias", fallback["next_attention_bias"]),
            change_macro_goal=data.get("change_macro_goal", fallback["change_macro_goal"]),
            lesson=data.get("lesson", fallback["lesson"]),
            novelty_score=clamp(data.get("novelty_score", fallback["novelty_score"])),
            repetition_detected=bool(data.get("repetition_detected", fallback["repetition_detected"])),
            store=bool(data.get("store", fallback["store"])),
        )


# ============================================================
# ORGANISM LOOP
# ============================================================

class MiniOrganism:
    def __init__(self):
        self.llm = LLM()
        self.world = WorldSimulator()
        self.memory = Memory()
        self.perception_interpreter = PerceptionInterpreter(self.llm)
        self.attention = AttentionSystem(self.llm)
        self.brain = Brain(self.llm)

        self.state = InternalState()
        self.focus = FocusState()
        self.goal = GoalState()

    def run_cycle(self):
        raw = self.world.observe_raw()
        perception = self.perception_interpreter.interpret(raw, self.memory)

        self.focus = self.attention.update(
            perception=perception,
            focus=self.focus,
            memory=self.memory,
            state=self.state,
        )

        if not self.focus.active():
            self.goal.micro_goal = "buscar um novo foco de atenção"
            self.goal.success_condition = "encontrar algo relevante"

        thought = self.brain.think(
            perception=perception,
            state=self.state,
            focus=self.focus,
            goal=self.goal,
            memory=self.memory,
        )

        action = self.brain.decide_action(
            thought=thought,
            perception=perception,
            focus=self.focus,
            state=self.state,
            memory=self.memory,
        )

        result = self.world.apply(action, self.focus)

        reflection = self.brain.reflect(
            perception=perception,
            thought=thought,
            action=action,
            result=result,
            focus=self.focus,
            goal=self.goal,
            memory=self.memory,
        )

        self.focus = self.attention.update(
            perception=perception,
            focus=self.focus,
            memory=self.memory,
            state=self.state,
        )

        if not self.focus.active():
            self.goal.micro_goal = "buscar um novo foco de atenção"
            self.goal.success_condition = "encontrar algo relevante"

        self._update_state(thought, result, reflection, perception)
        self._update_goal(thought, reflection)
        self._update_focus(reflection)

        self.memory.add({
            "cycle": perception.cycle,
            "raw_scene": perception.raw_scene,
            "scene_summary": perception.scene_summary,
            "focus_target": self.focus.target,
            "macro_goal": self.goal.macro_goal,
            "micro_goal": thought.micro_goal,
            "intent_type": thought.intent_type,
            "action": action.name,
            "result": result.outcome,
            "novelty": result.novelty,
            "progress": result.progress,
            "risk": result.risk,
            "reflection": reflection.summary,
            "lesson": reflection.lesson,
            "focus_decision": reflection.focus_decision,
            "avoid_target": reflection.avoid_target,
            "avoid_reason": reflection.avoid_reason,
            "return_condition": reflection.return_condition,
            "next_attention_bias": reflection.next_attention_bias,
        })

        self._print_cycle(raw, perception, thought, action, result, reflection)

    def _update_state(self, thought: Thought, result: ActionResult, reflection: Reflection, perception: Perception):
        repeated = reflection.repetition_detected
        low_novelty = result.novelty < 0.35
        low_progress = result.progress < 0.35
        rejected = reflection.focus_decision in ["abandon", "avoid_temporarily", "return_later"]

        if repeated or low_novelty or rejected:
            self.state.boredom = clamp(self.state.boredom + 0.10)
            self.state.curiosity = clamp(self.state.curiosity - 0.06)
        else:
            self.state.boredom = clamp(self.state.boredom - 0.05)
            self.state.curiosity = clamp(self.state.curiosity + 0.04)

        if low_progress:
            self.state.frustration = clamp(self.state.frustration + 0.08)
        else:
            self.state.frustration = clamp(self.state.frustration - 0.04)

        self.state.energy = clamp(self.state.energy - 0.025)
        self.state.caution = clamp((self.state.caution * 0.7) + (perception.risk * 0.3))

        if self.state.energy < 0.25:
            self.state.mood = "tired"
        elif self.state.frustration > 0.65:
            self.state.mood = "frustrated"
        elif self.state.boredom > 0.65:
            self.state.mood = "bored"
        elif self.state.caution > 0.65:
            self.state.mood = "cautious"
        else:
            self.state.mood = thought.mood

    def _update_goal(self, thought: Thought, reflection: Reflection):
        self.goal.micro_goal = thought.micro_goal
        self.goal.success_condition = thought.success_condition
        self.goal.age_cycles += 1

        if reflection.next_attention_bias:
            self.goal.micro_goal = reflection.next_attention_bias
            self.goal.success_condition = "perceber mudança relevante"

        if reflection.change_macro_goal:
            self.goal.macro_goal = reflection.change_macro_goal
            self.goal.age_cycles = 0

        if self.state.energy < 0.25:
            self.goal.macro_goal = "preservar energia e agir com calma"
        elif self.state.boredom > 0.75:
            self.goal.macro_goal = "buscar novidade para reduzir saturação"
        elif self.state.caution > 0.75:
            self.goal.macro_goal = "preservar segurança e entender riscos"

    def _update_focus(self, reflection: Reflection):
        if not self.focus.active():
            return

        if reflection.focus_decision == "keep":
            if reflection.keep_focus:
                self.focus.interest = clamp(self.focus.interest + 0.05)
            else:
                self.focus.interest = clamp(self.focus.interest - 0.15)

        elif reflection.focus_decision == "soften":
            self.focus.interest = clamp(self.focus.interest - 0.20)

        elif reflection.focus_decision in ["abandon", "avoid_temporarily", "return_later"]:
            self.focus.interest = clamp(self.focus.interest - 0.45)
            self.focus.reason = reflection.avoid_reason or "decidi reduzir esse foco por agora"

        else:
            self.focus.interest = clamp(self.focus.interest - 0.10)

        if self.focus.interest <= 0.25:
            self.focus = FocusState()
            self.goal.micro_goal = "buscar um novo foco de atenção"
            self.goal.success_condition = "encontrar algo relevante"

    def _print_cycle(self, raw, perception, thought, action, result, reflection):
        data = {
            "cycle": raw.cycle,
            "raw_world": asdict(raw),
            "perception": asdict(perception),
            "focus": asdict(self.focus),
            "goal": asdict(self.goal),
            "state": asdict(self.state),
            "thought": asdict(thought),
            "action": asdict(action),
            "result": asdict(result),
            "reflection": asdict(reflection),
            "recent_affective_memory": self.memory.recent_affective_memory(5),
        }

        print_box(
            f"CICLO {raw.cycle}",
            json.dumps(data, ensure_ascii=False, indent=2),
        )


# ============================================================
# MAIN
# ============================================================

def main():
    cycles = int(os.getenv("CYCLES", "10"))
    delay = float(os.getenv("DELAY", "1.0"))

    organism = MiniOrganism()

    print("\nMiniOrganism V2 iniciado.")
    print("Objetivo: validar cérebro genérico com LLM no loop cognitivo.")
    print("CTRL+C para parar.\n")

    try:
        for _ in range(cycles):
            organism.run_cycle()
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")


if __name__ == "__main__":
    main()