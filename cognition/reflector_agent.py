import json
import os
from collections import Counter
from typing import Any, Optional
from openai import OpenAI
from core.schemas import Reflection
from pydantic import BaseModel


class ReflectionOverride(BaseModel):
    override: bool = False
    intent_type: Optional[str] = None
    mood: Optional[str] = None
    intent: Optional[str] = None
    reason: Optional[str] = None




class ReflectorAgent:
    def __init__(self, model: Optional[str] = None):
        self.model = model or os.getenv("REFLECTOR_MODEL", "gpt-4o-mini")
        self.client = OpenAI()

    #new
    def review_before_action(self, world_state, thought, recent_context=None) -> ReflectionOverride:
        recent_context = recent_context or []

        decision = ReflectionOverride(
            override=False,
            reason="no_override_needed",
        )

        try:
            payload = {
                "world_state": self._safe_world_state(world_state),
                "thought": self._safe_object(thought),
                "recent_context": recent_context[-6:],
            }

            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eu sou meu ReflectorAgent antes da ação. "
                            "Minha função é revisar quando necessario minha intenção antes de executar. "
                            "Eu posso permitir a intenção original ou substituir por uma intenção mais inteligente apenas se necessario, "
                            "menos repetitiva e mais inteligente. "
                            "Eu penso sempre em primeira pessoa. "
                            "Eu respondo somente JSON válido em português."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Estou prestes a agir.

                        Dados atuais:
                        {json.dumps(payload, ensure_ascii=False, indent=2)}

                        Minha tarefa:
                        - revisar minha intenção apenas quando realmente necessário
                        - detectar risco físico real
                        - detectar repetição forte
                        - evitar movimento perigoso
                        - evitar bloquear minha iniciativa sem motivo
                        - decidir se devo sobrescrever minha intenção ou deixar o ExecutiveAgent escolher as ações

                        Regras:
                        - Na maioria dos ciclos, devo retornar override=false.
                        - Use override=true apenas se houver risco físico, repetição forte ou conflito evidente.
                        - Observe significa: parar a base e olhar ao redor com os servos.
                        - Explore significa: mover a base com prudência.
                        - Safe_stop significa: parar tudo por segurança.
                        - Se estou repetindo explore, não transforme automaticamente em observe; posso permitir o ExecutiveAgent variar a ação.
                        - Se vejo pessoa, criança, mão ou rosto, eu não preciso obrigatoriamente bloquear; só devo bloquear avanço se parecer próximo, arriscado ou invasivo.
                        - Se camera_summary está vazio, não force observe sempre; posso deixar o ExecutiveAgent decidir uma ação visual segura.
                        - Se não houver motivo forte para sobrescrever, retorne override=false.
                        - Não controle motores diretamente.
                        - Não gere actions.
                        - Apenas revise intent_type, intent e mood.
                        - Escreva intent sempre em português do Brasil.

                        Responda somente JSON válido:

                        {{
                        "override": true,
                        "intent_type": "observe | explore | interact | avoid | safe_stop | idle",
                        "intent": "frase curta em primeira pessoa",
                        "mood": "curious | bored | calm | alert | neutral",
                        "reason": "motivo curto"
                        }}
                        """
                    },
                ],
            )

            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)

            decision = ReflectionOverride(
                override=bool(data.get("override", False)),
                intent_type=data.get("intent_type"),
                intent=data.get("intent"),
                mood=data.get("mood"),
                reason=data.get("reason") or "llm_review",
            )

        except Exception as exc:
            decision = ReflectionOverride(
                override=False,
                reason=f"reflector_llm_failed: {exc}",
            )

        # Trava física obrigatória: segurança não depende da LLM
        front_distance = getattr(world_state, "front_distance_cm", None)

        if front_distance is not None and front_distance < 20:
            return ReflectionOverride(
                override=True,
                intent_type="safe_stop",
                intent="Tem algo perto demais à minha frente. Vou parar e observar com cuidado.",
                mood="alert",
                reason="hard_safety_front_distance",
            )

        return decision
    
    
    def run(self, world_state, thought, plan, result, recent_context=None) -> Reflection:
        recent_context = recent_context or []

        fallback = self._fallback_reflection(
            world_state=world_state,
            thought=thought,
            plan=plan,
            result=result,
            recent_context=recent_context,
        )

        try:
            payload = self._build_payload(
                world_state=world_state,
                thought=thought,
                plan=plan,
                result=result,
                recent_context=recent_context,
            )

            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eu sou meu mecanismo interno de reflexão. "
                            "Eu avalio o que acabei de perceber, decidir e executar. "
                            "Eu sempre penso em primeira pessoa. "
                            "Eu nunca falo sobre 'o organismo' em terceira pessoa. "
                            "Eu respondo apenas JSON válido."
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

            return Reflection(
                episode_summary=data.get("episode_summary") or fallback.episode_summary,
                lesson=data.get("lesson"),
                repetition_detected=bool(data.get("repetition_detected", False)),
                suggested_next_focus=data.get("suggested_next_focus"),
                suggested_mood_shift=data.get("suggested_mood_shift"),
                avoid_next_intent_type=data.get("avoid_next_intent_type"),
                reflection_hint=data.get("reflection_hint"),
                store_structured=bool(data.get("store_structured", True)),
                novelty_score=float(data.get("novelty_score", fallback.novelty_score)),
                policy_feedback=data.get("policy_feedback") or fallback.policy_feedback,
            )

        except Exception as exc:
            fallback.reflection_hint = (
                fallback.reflection_hint
                or f"Não consegui refletir com clareza neste ciclo, mas devo evitar repetir o mesmo padrão sem ganhar nova informação. Erro: {exc}"
            )
            return fallback

    def _build_payload(self, world_state, thought, plan, result, recent_context) -> dict[str, Any]:
        return {
            "world_state": self._safe_world_state(world_state),
            "thought": self._safe_object(thought),
            "plan": self._safe_object(plan),
            "result": self._safe_object(result),
            "recent_context": recent_context[-6:],
        }

    def _build_prompt(self, payload: dict[str, Any]) -> str:
        return f"""
Eu acabei de executar um ciclo interno.

Minha tarefa agora é refletir sobre mim mesmo e preparar melhor o próximo ciclo.

Eu devo avaliar:
- se fiquei preso em repetição
- se minha intenção combinou com meu humor
- se minha ação gerou novidade
- se estou apenas observando sem mudar nada
- se devo mudar meu foco no próximo ciclo
- se devo evitar algum intent_type no próximo ciclo

Regras importantes:
- Escreva sempre em primeira pessoa.
- Nunca use "o organismo", "ele", "robô" ou terceira pessoa.
- Eu não controlo motores diretamente aqui.
- Eu apenas gero reflexão interna para influenciar minha próxima decisão.
- Se eu estiver bored, com baixa novidade, e continuei em observe ou idle, eu devo reconhecer isso como repetição improdutiva.
- Segurança física continua sendo prioridade: se houver obstáculo perto ou erro crítico, devo recomendar foco seguro.

Dados do ciclo:
{json.dumps(payload, ensure_ascii=False, indent=2)}

Responda somente JSON válido com exatamente estes campos:

{{
  "episode_summary": "resumo curto em primeira pessoa",
  "lesson": "aprendizado em primeira pessoa ou null",
  "repetition_detected": true,
  "suggested_next_focus": "meu próximo foco em primeira pessoa ou null",
  "suggested_mood_shift": "curious | bored | calm | alert | neutral ou null",
  "avoid_next_intent_type": "observe | idle | explore | approach | avoid | safe_stop ou null",
  "reflection_hint": "orientação interna forte em primeira pessoa ou null",
  "store_structured": true,
  "novelty_score": 0.0,
  "policy_feedback": {{
    "context_signature": "texto curto",
    "action_signature": "texto curto",
    "score_delta": 0.0
  }}
}}
"""

    def _fallback_reflection(self, world_state, thought, plan, result, recent_context=None) -> Reflection:
        recent_context = recent_context or []

        recent_intent_types = [
            item.get("intent_type")
            for item in recent_context
            if isinstance(item, dict) and item.get("intent_type")
        ]

        counter = Counter(recent_intent_types)
        current_intent_type = getattr(thought, "intent_type", None)

        repetition_detected = False
        suggested_next_focus = None
        suggested_mood_shift = None
        avoid_next_intent_type = None
        reflection_hint = None

        if current_intent_type and counter.get(current_intent_type, 0) >= 3:
            repetition_detected = True
            avoid_next_intent_type = current_intent_type
            suggested_next_focus = "Quero mudar meu foco para gerar nova informação."
            suggested_mood_shift = "curious"
            reflection_hint = (
                f"Eu repeti o intent_type '{current_intent_type}' várias vezes sem ganhar informação clara. "
                "No próximo ciclo, devo evitar repetir isso e buscar uma percepção nova com segurança."
            )

        lesson = None
        novelty_score = 0.1

        if world_state.front_distance_cm is not None and world_state.front_distance_cm < 20:
            lesson = "Quando há obstáculo perto, devo priorizar inspeção cuidadosa antes de qualquer movimento."
            novelty_score = 0.3

        if world_state.last_error:
            lesson = "Quando encontro erro crítico, devo entrar em segurança e reduzir ações arriscadas."
            novelty_score = 0.6

        if repetition_detected:
            novelty_score = max(novelty_score, 0.2)

        return Reflection(
            episode_summary=(
                f"Eu tive intent_type={getattr(thought, 'intent_type', None)}; "
                f"intent={thought.intent}; result={result.status}; "
                f"actions={result.completed_actions}"
            ),
            lesson=lesson,
            repetition_detected=repetition_detected,
            suggested_next_focus=suggested_next_focus,
            suggested_mood_shift=suggested_mood_shift,
            avoid_next_intent_type=avoid_next_intent_type,
            reflection_hint=reflection_hint,
            store_structured=True,
            novelty_score=novelty_score,
            policy_feedback={
                "context_signature": f"mode={world_state.mode};goal={world_state.current_goal}",
                "action_signature": getattr(thought, "intent_type", thought.intent),
                "score_delta": 0.1 if result.status == "success" and not repetition_detected else -0.1,
            },
        )

    def _safe_world_state(self, world_state) -> dict[str, Any]:
        return {
            "mode": getattr(world_state, "mode", None),
            "current_goal": getattr(world_state, "current_goal", None),
            "front_distance_cm": getattr(world_state, "front_distance_cm", None),
            "battery": getattr(world_state, "battery", None),
            "camera_summary": getattr(world_state, "camera_summary", None),
            "audio": getattr(world_state, "audio", None),
            "last_error": getattr(world_state, "last_error", None),
        }

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
