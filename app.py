import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from api.server import app as base_app, register_runtime
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

runtime_tasks: list[asyncio.Task] = []


register_runtime(
    state_store=state_store,
    sensor_hub=sensor_hub,
    executor=executor,
    memory_manager=memory_manager,
    last_thought=None,
    last_plan=None,
    last_result=None,
    last_reflection=None,
)


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
    first_cycle = True

    while True:
        snapshot = sensor_hub.get()
        current_state = state_store.get()

        perception = perceptor.run(snapshot)
        world_model.state = current_state
        world_state = world_model.update(snapshot, perception)

        if first_cycle and world_state.mode == "booting":
            world_state = world_state.copy(update={"mode": "idle", "current_goal": "monitor safely"})
            first_cycle = False

        state_store.update(**world_state.model_dump())

        thought = thinker.run(world_state)
        plan = compiler.run(thought)
        result = executor.run_plan(plan, world_state)
        reflection = reflector.run(world_state, thought, plan, result)

        register_runtime(
            last_thought=thought,
            last_plan=plan,
            last_result=result,
            last_reflection=reflection,
        )

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


@asynccontextmanager
async def lifespan(_: FastAPI):
    state_store.update(mode="booting", current_goal="initialize organism")

    realtime_task = asyncio.create_task(realtime_loop(), name="realtime_loop")
    cognitive_task = asyncio.create_task(cognitive_loop(), name="cognitive_loop")

    runtime_tasks.extend([realtime_task, cognitive_task])

    try:
        yield
    finally:
        for task in runtime_tasks:
            task.cancel()

        await asyncio.gather(*runtime_tasks, return_exceptions=True)
        runtime_tasks.clear()


app = FastAPI(title=base_app.title, lifespan=lifespan)

for route in base_app.router.routes:
    app.router.routes.append(route)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
