from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Numeric, Integer, Boolean, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(200), nullable = False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable = True)
    publisher: Mapped[str | None] = mapped_column(String(100), nullable = True)

    min_players: Mapped[int | None] = mapped_column(Integer, nullable = True)
    max_players: Mapped[int | None] = mapped_column(Integer, nullable = True)
    play_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable = True)
    min_age: Mapped[int | None] = mapped_column(Integer, nullable = True)

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable = False)
    stock: Mapped[int] = mapped_column(Integer, default = 0, nullable = False)
    is_active: Mapped[bool] = mapped_column(Boolean, default = True, nullable = False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OutboxMessage(Base):
    __tablename__ = "outbox_messages"

    id: Mapped[int] = mapped_column(primary_key = True)

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    routing_key: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

