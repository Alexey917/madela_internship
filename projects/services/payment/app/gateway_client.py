import httpx, logging
from decimal import Decimal

from app.config import settings

from tenacity import (
     AsyncRetrying,
     RetryError,
     retry_if_exception_type,
     stop_after_attempt,
     wait_exponential
)

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)


class GateWayError(Exception):
    """Сетевая ошибка шлюза — retry"""

class GatewayResponse:
    def __init__(self, external_id: str, status: str, failure_reason: str | None = None):
        self.external_id = external_id
        self.status = status
        self.failure_reason = failure_reason


async def _charge_once(order_id: str, amount: Decimal) -> GatewayResponse:
      """Одна попытка. Бросает GatewayError при сетевой ошибке."""
      async with httpx.AsyncClient(timeout=5.0) as client:
           response = await client.post(
                f"{settings.mock_gateway_url}/charge",
                json={"order_id": order_id, "amount": str(amount)},
           )

      if response.status_code >= 500:
          raise GateWayError(f"Gateway returned {response.status_code}")

      data = response.json()

      return GatewayResponse(
          external_id = data["external_id"],
          status = data["status"],
          failure_reason = data.get("failure_reason")
      )


async def charge_with_retry(order_id: str, amount: Decimal) -> GatewayResponse:
    """
    Вызывает шлюз с retry при сетевых ошибках.
    Экспоненциальная задержка: 1 → 2 → 4 → 8 сек (4 попытки).
    """
    try:
        async for attempt in AsyncRetrying(
            stop = stop_after_attempt(4),
            wait = wait_exponential(multiplier=1, min=1, max=8),
            retry = retry_if_exception_type(GateWayError),
            reraise = True
        ):
            with attempt:
                logger.info(
                    "Charging gateway: order_id=%s, attempt=%d",
                    order_id, attempt.retry_state.attempt_number,
                )
                result = await  _charge_once(order_id, amount)
                return result
    except RetryError as e:
        logger.error("Gateway retries exhausted: %s", e)
        raise

    raise RuntimeError("Retry loop exited unexpectedly")
            

