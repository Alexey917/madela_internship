from pydantic import BaseModel, Field, ConfigDict

from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    name: str  = Field(..., min_length=1, max_length=200)
    description: str | None = Field(max_length=1000, default=None)
    publisher: str | None = Field(max_length=100, default=None)
    min_players: int | None = Field(ge=1, le=20, default=None)
    max_players: int | None  = Field(ge=1, le=20, default=None)
    play_time_minutes: int | None = Field(ge=1, le=1000, default=None)
    min_age: int | None  = Field(ge=0, le=100, default=None)
    stock: int = Field(default=0, ge=0)
    price: Decimal  = Field(..., gt=0, decimal_places=2)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    name: str  = Field(min_length=1, max_length=200, default=None)
    description: str | None = Field(max_length=1000, default=None)
    publisher: str | None = Field(max_length=100, default=None)
    min_players: int | None = Field(ge=1, le=20, default=None)
    max_players: int | None  = Field(ge=1, le=20, default=None)
    play_time_minutes: int | None = Field(ge=1, le=1000, default=None)
    min_age: int | None  = Field(ge=0, le=100, default=None)
    stock: int | None = Field(ge=0, default=None)
    price: Decimal  = Field(gt=0, decimal_places=2, default=None)
    is_active: bool | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    items: list[ProductRead]
    page: int
    size: int
    total: int
