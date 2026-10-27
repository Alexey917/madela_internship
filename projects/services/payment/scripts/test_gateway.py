import asyncio
from decimal import Decimal

from app.gateway_client import charge_with_retry


async def main() -> None:
    # 10 раз — увидим, как retry спасает от 500
    for i in range(10):
        try:
            result = await charge_with_retry(order_id=f"test-{i}", amount=Decimal("100.00"))
            print(f"[{i}] {result.status} — {result.external_id}")
        except Exception as e:
            print(f"[{i}] Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())