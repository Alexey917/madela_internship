from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class StockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    available: int
    reserved: int
    product_id: int
    created_at: datetime
    updated_at: datetime


class StockReserveRequest(BaseModel):
    product_id: int = Field(..., ge=1)
    quantity: int = Field(..., gt=0)


class StockCommitRequest(BaseModel):
    product_id: int = Field(..., ge=1)
    quantity: int = Field(..., gt=0)


class StockReleaseRequest(BaseModel):
    product_id: int = Field(..., ge=1)
    quantity: int = Field(..., gt=0)