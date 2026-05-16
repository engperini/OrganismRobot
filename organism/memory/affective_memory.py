import unicodedata


class AffectiveMemory:
    def __init__(self):
        self.items = []

    def _normalize(self, text):
        text = str(text or "").lower().strip()
        text = unicodedata.normalize("NFD", text)
        text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
        return text

    def remember(self, item):
        self.items.append(item)
        if len(self.items) > 50:
            self.items = self.items[-50:]

    def recent(self, limit=5):
        return self.items[-limit:]

    def repeated_scene(self, limit=4):
        recent = self.recent(limit)
        if len(recent) < 3:
            return False

        descriptions = []

        for item in recent:
            perception = item.get("perception", {})
            camera = perception.get("camera_summary") or {}
            llm = camera.get("llm_description") or {}
            desc = self._normalize(llm.get("description", ""))
            descriptions.append(desc)

        keywords = [
            "carregamento",
            "circulo",
            "circular",
            "preto",
            "branco",
            "loading",
            "icone",
            "fundo preto",
        ]

        score = 0

        for desc in descriptions[-3:]:
            if any(k in desc for k in keywords):
                score += 1

        return score >= 3

    def last_action_name(self):
        if not self.items:
            return None

        last = self.items[-1]
        thought = last.get("thought", {})
        action = thought.get("action", {})
        return action.get("name")
