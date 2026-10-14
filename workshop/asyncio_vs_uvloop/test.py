import sys
import asyncio
import uvloop

uvloop.install()

async def main():
    print("✅ UVLOOP РАБОТАЕТ!")
    print(f"Версия Python: {sys.version}")

asyncio.run(main())
