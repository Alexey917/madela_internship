import asyncio

from .db import create_tables, engine

async def main() -> None:
    await create_tables()
    await engine.dispose()


asyncio.run(main())