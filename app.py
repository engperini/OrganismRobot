import asyncio
from api.server import app
from core.state_store import StateStore
from realtime.sensor_hub import SensorHub
from realtime.distance_loop import read_distance
from realtime.battery_loop import read_battery_pct
from realtime.motor_state_loop import read_motor_state
from realtime.servo_state_loop import read_servo_state
from realtime.error_loop import read_last_error
from realtime.camera_frame_loop import capture_frame_summary
from realtime.audio_loop_stub import read_audio_summary
from cognition.perceptor_agent import PerceptorAgent
from cognition.world_model import WorldModel
from cognition.thinker_agent import ThinkerAgent
from cognition.compiler_agent import CompilerAgent
from cognition.reflector_agent import ReflectorAgent
from actuation.executor import Executor
from memory.short_term import ShortTermMemory
from memory.sqlite_store import SQLiteStore
from memory.memory_manager import MemoryManager

state_store = StateStore()
sensor_hub = SensorHub()
perceptor = PerceptorAgent()
world_model = WorldModel()
thinker = ThinkerAgent()
compiler = CompilerAgent()
reflector = ReflectorAgent()
executor = Executor()
short_term = ShortTermMemory()
sqlite_store = SQLiteStore()
memory_manager = MemoryManager(sqlite_store, short_term)

async def realtime_loop():
    while True:
        distance = await read_distance()
        battery = await read_battery_pct()
        motors = await read_motor_state()
        servos = await read_servo_state()
        last_error = await read_last_error()
        camera_summary = await capture_frame_summary()
        audio_summary = await read_audio_summary()

        sensor_hub.update(
            distance_front_cm=distance,
            battery_pct=battery,
            last_error=last_error,
            camera_summary=camera_summary,
            audio_summary=audio_summary,
            **motors,
            **servos,
        )
        await asyncio.sleep(0.5)

async def cognitive_loop():
    while True:
        snapshot = sensor_hub.get()
        perception = perceptor.run(snapshot)
        world_state = world_model.update(snapshot, perception)
        state_store.update(**world_state.model_dump())

        thought = thinker.run(world_state)
        plan = compiler.run(thought)
        result = executor.run_plan(plan, world_state)
        reflection = reflector.run(world_state, thought, plan, result)

        memory_manager.remember({
            "snapshot": snapshot.model_dump(),
            "perception": perception.model_dump(),
            "thought": thought.model_dump(),
            "plan": plan.model_dump(),
            "result": result.model_dump(),
            "reflection": reflection.model_dump(),
        })
        memory_manager.persist_event(str(perception.model_dump()))
        memory_manager.persist_episode(thought, result, reflection)

        await asyncio.sleep(1.0)

async def main():
    await asyncio.gather(
        realtime_loop(),
        cognitive_loop(),
    )

if __name__ == "__main__":
    import uvicorn
    asyncio.get_event_loop().create_task(main())
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=False)
