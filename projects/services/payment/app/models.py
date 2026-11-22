import enum

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, func, String, Numeric, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key = True)
    order_id: Mapped[str] = mapped_column(String(100), nullable = False, index = True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable = False)
    payment_status: Mapped[Enum] = mapped_column(
        Enum(PaymentStatus, name = "payment_status", native_enum = False),
        nullable = False,
        default = PaymentStatus.PENDING
    )
    external_id: Mapped[str | None] = mapped_column(String(200), nullable = True)
    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable = True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True), 
        server_default = func.now(),
        nullable = False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True), 
        server_default = func.now(),
        onupdate = func.now(),
        nullable = False
    )

class OutboxMessage(Base):
    __tablename__ = "outbox_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    routing_key: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

