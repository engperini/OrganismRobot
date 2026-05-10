import json
import os
from typing import Any, Optional

from openai import OpenAI

from core.schemas import ExecutablePlan, PlanAction


class ExecutiveAgent:
    def __init__(self, model: Optional[str] = None):
        self.model = model or os.getenv("EXECUTIVE_MODEL", "gpt-4o-mini")
        self.client = OpenAI()

        self.available_tools = [
            "motors.stop",
            "motors.forward",
            "motors.backward",
            "motors.turn_left",
            "motors.turn_right",
            "servos.center",
            "servos.random",
            "servos.look",
        ]

    def run(
        self,
        world_state,
        thought,
        reflection_override=None,
        recent_context=None,
    ) -> ExecutablePlan:
        recent_context = recent_context or []

        fallback_plan = self._fallback_plan(world_state, thought)

        try:
            payload = {
                "world_state": self._json_safe(self._safe_object(world_state)),
                "thought": self._json_safe(self._safe_object(thought)),
                "reflection_override": self._json_safe(self._safe_object(reflection_override)),
                "recent_context": recent_context[-5:],
                "available_tools": self.available_tools,
            }

            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eu sou o ExecutiveAgent de um robô físico autônomo. "
                            "Minha função é transformar intenção interna em pequenas ações corporais concretas. "
                            "Eu escolho tools disponíveis, mas não invento tools novas. "
                            "Eu devo ser curioso, prudente e evitar repetição burra. "
                            "Eu respondo somente JSON válido."
                        ),
                    },
                    {
                        "role": "user",
                        "content": self._build_prompt(payload),
                    },
                ],
            )

            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)

            actions = self._parse_actions(data)

            if not actions:
                return fallback_plan

            return ExecutablePlan(
                plan_id="plan_executive_llm",
                actions=actions,
                policy={
                    "source": "executive_agent",
                    "source_intent_type": getattr(thought, "intent_type", None),
                    "confidence": getattr(thought, "confidence", 0.5),
                    "urgency": getattr(thought, "urgency", 0.0),
                    "curiosity": getattr(thought, "curiosity", 0.0),
                    "reason": data.get("reason"),
                },
                expression={
                    "mood": getattr(thought, "mood", None),
                    "attention_target": getattr(thought, "attention_target", None),
                },
                voice_hint=data.get("voice_hint") or getattr(thought, "external_message", None),
                store_memory=getattr(thought, "store_candidate", False),
                memory_hint=getattr(thought, "intent", None),
            )

        except Exception as exc:
            print(f"[executive] LLM failed, using fallback: {exc}")
            return fallback_plan

    def _build_prompt(self, payload: dict[str, Any]) -> str:
        return f"""
Estou prestes a agir no mundo físico.

Dados atuais:
{json.dumps(payload, ensure_ascii=False, indent=2)}

Minha tarefa:
- escolher ações corporais concretas
- usar apenas tools disponíveis
- transformar intenção interna em comportamento físico claro
- variar minhas ações corporais
- evitar repetir sempre a mesma ação
- ser prudente perto de pessoas, crianças, mãos ou rostos
- escrever voice_hint em português do Brasil

Definições obrigatórias:
- observe = olhar ao redor sem mover a base. Use motors.stop + servos.random.
- explore = explorar fisicamente o ambiente. Use pelo menos uma ação de base: motors.forward, motors.backward, motors.turn_left ou motors.turn_right.
- safe_stop = parada segura. Use motors.stop + servos.center.
- avoid = afastar ou desviar. Use motors.backward, motors.turn_left ou motors.turn_right.
- interact = parar a base e prestar atenção socialmente. Use motors.stop e movimento leve de servo.

Regras:
- Se intent_type for safe_stop: use motors.stop e servos.center.
- Se intent_type for observe: use motors.stop e servos.random.
- Se intent_type for explore: use pelo menos uma ação de base, exceto se houver risco concreto.
- Se eu não mover a base em explore, o campo reason deve explicar o risco concreto.
- Não chame exploração visual parada de explore; isso é observe.
- Se front_distance_cm estiver abaixo de 20, não avance.
- Se front_distance_cm estiver entre 20 e 30, prefira motors.turn_left, motors.turn_right ou motors.backward.
- Se front_distance_cm estiver acima de 30 ou ausente, posso usar motors.forward, motors.turn_left, motors.turn_right ou motors.backward.
- Movimento deve ser curto, normalmente duration entre 0.5 e 2.0 segundos.
- Use no máximo 3 ações.
- Não invente tools.

Responda somente JSON válido:

{{
  "actions": [
    {{
      "tool": "servos.random",
      "args": {{}}
    }},
    {{
      "tool": "motors.turn_left",
      "args": {{"duration": 1.0}}
    }}
  ],
  "voice_hint": "frase curta em português",
  "reason": "motivo curto"
}}
"""

#     def _build_prompt(self, payload: dict[str, Any]) -> str:
#         return f"""
# Estou prestes a agir no mundo físico.

# Dados atuais:
# {json.dumps(payload, ensure_ascii=False, indent=2)}

# Minha tarefa:
# - escolher ações corporais concretas
# - usar apenas tools disponíveis
# - evitar repetir sempre motors.forward
# - usar servos.random quando eu quiser procurar visualmente sem mover a base
# - usar motors.stop quando eu precisar parar antes de observar
# - usar motors.backward quando eu precisar me afastar
# - usar motors.turn_left ou motors.turn_right quando fizer mais sentido girar do que avançar
# - ser prudente perto de pessoas, crianças, mãos ou rostos
# - escrever voice_hint em português do Brasil

# Regras:
# - Se intent_type for safe_stop: use motors.stop e servos.center.
# - Se eu quiser observar parado: use motors.stop e servos.center.
# - Se eu quiser procurar novidade visual sem mover a base: use motors.stop e servos.random.
# - Se eu quiser explorar com a base: escolha forward, backward, turn_left ou turn_right.
# - Não avance se front_distance_cm parecer baixo.
# - Movimento deve ser curto, normalmente duration entre 0.5 e 2.0 segundos.
# - Use no máximo 3 ações.
# - Não invente tools.

# Responda somente JSON válido:

# {{
#   "actions": [
#     {{
#       "tool": "motors.stop",
#       "args": {{}}
#     }},
#     {{
#       "tool": "servos.random",
#       "args": {{}}
#     }}
#   ],
#   "voice_hint": "frase curta em português",
#   "reason": "motivo curto"
# }}
# """

    def _parse_actions(self, data: dict[str, Any]) -> list[PlanAction]:
        actions: list[PlanAction] = []

        for item in data.get("actions", []):
            if not isinstance(item, dict):
                continue

            tool = item.get("tool")
            args = item.get("args") or {}

            if tool not in self.available_tools:
                continue

            if not isinstance(args, dict):
                args = {}

            if tool.startswith("motors."):
                duration = args.get("duration")
                if duration is not None:
                    try:
                        args["duration"] = max(0.1, min(float(duration), 2.0))
                    except Exception:
                        args["duration"] = 1.0

            actions.append(
                PlanAction(
                    tool=tool,
                    args=args,
                    timeout_s=3.0,
                )
            )

        return actions

    def _fallback_plan(self, world_state, thought) -> ExecutablePlan:
        intent_type = (getattr(thought, "intent_type", "") or "").lower()
        front_distance = getattr(world_state, "front_distance_cm", None)

        if "safe_stop" in intent_type:
            actions = [
                PlanAction(tool="motors.stop"),
                PlanAction(tool="servos.center"),
            ]

        elif front_distance is not None and front_distance < 20:
            actions = [
                PlanAction(tool="motors.stop"),
                PlanAction(tool="servos.random"),
            ]



        elif "explore" in intent_type:
            actions = [
                PlanAction(tool="servos.random"),
                PlanAction(tool="motors.forward", args={"duration": 1.0}),
            ]

        elif "backward" in intent_type or "retreat" in intent_type:
            actions = [
                PlanAction(tool="motors.backward", args={"duration": 1.0}),
            ]

        elif "turn_left" in intent_type:
            actions = [
                PlanAction(tool="motors.turn_left", args={"duration": 1.0}),
            ]

        elif "turn_right" in intent_type:
            actions = [
                PlanAction(tool="motors.turn_right", args={"duration": 1.0}),
            ]

        else:
            actions = [
                PlanAction(tool="motors.stop"),
                PlanAction(tool="servos.random"),
            ]

        return ExecutablePlan(
            plan_id="plan_executive_fallback",
            actions=actions,
            policy={
                "source": "executive_fallback",
                "source_intent_type": intent_type,
                "front_distance_cm": front_distance,
            },
            expression={
                "mood": getattr(thought, "mood", None),
                "attention_target": getattr(thought, "attention_target", None),
            },
            voice_hint=getattr(thought, "external_message", None),
            store_memory=getattr(thought, "store_candidate", False),
            memory_hint=getattr(thought, "intent", None),
        )

    def _safe_object(self, obj) -> Any:
        if obj is None:
            return None
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        if isinstance(obj, (dict, list, str, int, float, bool)):
            return obj
        return str(obj)

    def _json_safe(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: self._json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._json_safe(v) for v in obj]
        elif hasattr(obj, "isoformat"):
            return obj.isoformat()
        return obj
