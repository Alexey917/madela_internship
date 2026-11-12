from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, UniqueConstraint
from datetime import datetime

from app.db import Base

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint("event_type", "order_id", name="uq_notification_event_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(100),nullable=False)
    order_id: Mapped[int] = mapped_column(nullable=False, index=True)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )