from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_notification(
        self,
        event_type: str,
        order_id: int,
        message: str,
    ) -> Notification | None:
        # Проверяем на дубликат
        existing = await self.session.execute(
            select(Notification).where(
                Notification.event_type == event_type,
                Notification.order_id == order_id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            return None

        notification = Notification(
            event_type=event_type,
            order_id=order_id,
            message=message,
        )
        self.session.add(notification)
        try:
            await self.session.commit()
        except IntegrityError:
            # Race condition: другой consumer успел вставить
            await self.session.rollback()
            return None

        await self.session.refresh(notification)
        return notification

    async def list_by_order(self, order_id: int) -> list[Notification]:
        result = await self.session.execute(
            select(Notification).where(Notification.order_id == order_id).order_by(Notification.id)
        )
        return list(result.scalars().all())