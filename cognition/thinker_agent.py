from core.schemas import Thought

class ThinkerAgent:
    def run(self, world_state, memories=None) -> Thought:
        memories = memories or []

        if world_state.last_error:
            return Thought(
                assessment="There is a recent critical error.",
                intent="safe_stop",
                strategy=["stop", "wait"],
                mood="sleepy",
                store_candidate=True,
                why_store="Critical error detected.",
            )

        if world_state.front_distance_cm is not None and world_state.front_distance_cm < 20:
            return Thought(
                assessment="There is an obstacle ahead.",
                intent="inspect",
                strategy=["look_left", "look_right", "wait"],
                mood="curious",
                store_candidate=False,
            )

        if world_state.mode == "explore":
            return Thought(
                assessment="Environment seems clear enough for light exploration.",
                intent="explore",
                strategy=["explore_step"],
                mood="curious",
                store_candidate=False,
            )

        return Thought(
            assessment="Environment stable.",
            intent="idle",
            strategy=["wait"],
            mood="bored",
            store_candidate=False,
        )
