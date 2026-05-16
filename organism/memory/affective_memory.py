class AffectiveMemory:
    def __init__(self):
        self.items = []

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
            desc = llm.get("description", "")
            descriptions.append(desc.lower().strip())

        if len(descriptions) < 3:
            return False

        keywords = ["carregamento", "círculo", "circular", "preto", "branco", "loading"]
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
