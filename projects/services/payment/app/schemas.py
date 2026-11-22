from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime

from app.models import PaymentStatus


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: str
    amount: Decimal
    payment_status: PaymentStatus
    external_id: str | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime
    

class PaymentCreate(BaseModel):
    order_id: str = Field(..., min_length=1, max_length=100)
    amount: Decimal = Field(..., gt=0, decimal_places=2)


class PaymentRefund(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class PaymentWebhook(BaseModel):
    payment_id: int
    status: str
    external_id: str | None = None
    failure_reason: str | None = None