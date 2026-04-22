from core.schemas import InnerVoiceMessage, WorldState


class InnerVoice:
    def render_message(
        self,
        world_state: WorldState,
        voice_hint: str | None = None,
    ) -> InnerVoiceMessage:
        if voice_hint:
            return InnerVoiceMessage(text=voice_hint)

        if world_state.mode == "safe_stop":
            return InnerVoiceMessage(text="Melhor parar agora.")

        if "front_blocked" in world_state.risk_flags:
            return InnerVoiceMessage(text="Melhor não ir agora.")

        if world_state.mood == "sleepy":
            return InnerVoiceMessage(text="Tô com sono.")
        if world_state.mood == "curious":
            return InnerVoiceMessage(text="Hmm… deixa eu ver.")
        if world_state.mood == "bored":
            return InnerVoiceMessage(text="Que tédio...")

        return InnerVoiceMessage(text="Tô só observando.")
