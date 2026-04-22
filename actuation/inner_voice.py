from core.schemas import InnerVoiceMessage

class InnerVoice:
    def speak(self, mood: str | None = None, intent: str | None = None, risk_flags: list[str] | None = None, voice_hint: str | None = None) -> InnerVoiceMessage:
        risk_flags = risk_flags or []

        if voice_hint:
            return InnerVoiceMessage(text=voice_hint)

        if "front_blocked" in risk_flags:
            return InnerVoiceMessage(text="Melhor não ir agora.")

        if "critical_error" in risk_flags:
            return InnerVoiceMessage(text="Hmm... algo deu errado.")

        if mood == "sleepy":
            return InnerVoiceMessage(text="Tô com sono...")

        if mood == "bored":
            return InnerVoiceMessage(text="Que tédio...")

        if mood == "curious" or intent in {"explore", "inspect", "investigate"}:
            return InnerVoiceMessage(text="Hmm... deixa eu ver.")

        return InnerVoiceMessage(text="Só observando.")
