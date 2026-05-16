from organism.adapters.real_world_adapter import RealWorldAdapter
from organism.cognition.brain_core import BrainCore
from organism.state.internal_state import InternalState
from organism.memory.affective_memory import AffectiveMemory
import time


def main():
    print("[runtime] Organism runtime booting...")

    world = RealWorldAdapter()
    brain = BrainCore()
    state = InternalState()
    memory = AffectiveMemory()

    while True:
        perception = world.observe()

        thought = brain.think(
            world=perception,
            state=state,
            memory=memory,
        )

        print("")
        print("===================================================")
        print("[PERCEPTION]")
        print(perception)

        print("")
        print("[THOUGHT]")
        print(thought)

        memory.remember({
            "perception": perception,
            "thought": thought,
        })

        time.sleep(2)


if __name__ == "__main__":
    main()
