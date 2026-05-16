import time

from organism.adapters.real_world_adapter import RealWorldAdapter
from organism.cognition.brain_core import BrainCore
from organism.state.internal_state import InternalState
from organism.memory.affective_memory import AffectiveMemory
from organism.actuation.hardware_bridge import HardwareBridge


def main():
    print("[runtime] Organism runtime booting...")

    world = RealWorldAdapter()
    brain = BrainCore()
    state = InternalState()
    memory = AffectiveMemory()
    hardware = HardwareBridge()

    try:
        while True:
            perception = world.observe()

            thought = brain.think(
                world=perception,
                state=state,
                memory=memory,
            )

            action_result = hardware.execute(thought["action"])

            reflection = brain.reflect_after_action(
                action_result=action_result,
                state=state,
            )

            memory.remember({
                "perception": perception,
                "thought": thought,
                "action_result": action_result,
                "reflection": reflection,
            })

            print("")
            print("===================================================")
            print("[PERCEPTION]")
            print(perception)

            print("")
            print("[THOUGHT]")
            print(thought)

            print("")
            print("[ACTION_RESULT]")
            print(action_result)

            print("")
            print("[REFLECTION]")
            print(reflection)

            time.sleep(2)

    except KeyboardInterrupt:
        print("[runtime] stopped by user")

    finally:
        hardware.shutdown()


if __name__ == "__main__":
    main()
