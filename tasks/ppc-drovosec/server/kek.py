
import asyncio

import src.connections as connections


async def scheduler():
    while True:
        connections.reset_connections()
        await asyncio.sleep(600)


async def main():
    task = asyncio.create_task(scheduler())
    await task


asyncio.run(main())