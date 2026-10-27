import random
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/mock-gateway", tags=["mock-gateway"])

class ChargeRequest(BaseModel):
    order_id: str
    amount: Decimal = Field(..., gt=0)


class ChargeResponse(BaseModel):
    external_id: str
    status: str
    failure_reason: str | None = None


@router.post("/charge", response_model = ChargeResponse)
async def charge(data: ChargeRequest) -> ChargeResponse:
    """ 
    Эмуляция платежного шлюза
    - 80% - success
    - 20% - fail 
    - 5% - имитация 500 (для retry)
    """

    roll = random.random()

    if roll < 0.05:
        # Имитация сетевой ошибки — 500
        raise HTTPException(status_code = 500, detail = "Gateway timeout")

    if roll < 0.20:
        # Карта отклонена
        return ChargeResponse(
            external_id=f"ch_mock_{data.order_id}",
            status="failed",
            failure_reason="insufficient_funds",
        )

    return ChargeResponse(
        external_id=f"ch_mock_{data.order_id}",
        status="succeeded",
    )