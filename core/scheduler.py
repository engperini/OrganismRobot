import asyncio

async def run_loop(coro, interval: float):
    while True:
        await coro()
        await asyncio.sleep(interval)
