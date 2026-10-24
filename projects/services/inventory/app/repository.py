from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Stock

class StockRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def get(self, product_id: int) -> Stock | None:
        stock = await self.session.execute(select(Stock).where(Stock.product_id  == product_id))
        return stock.scalar_one_or_none()


    async def get_for_update(self, product_id: int) -> Stock | None:
        """Блокирует строку до конца транзакции (SELECT ... FOR UPDATE)."""
        stock = await self.session.execute(select(Stock).where(Stock.product_id  == product_id).with_for_update())
        return stock.scalar_one_or_none()


    async def reserve(self, product_id: int, quantity: int) -> Stock | None: 
        """Резервирует quantity. Возвращает Stock или None, если недостаточно."""
        stock = await self.get_for_update(product_id)

        if stock is None:
            return None

        if stock.available < quantity:
            return None

        stock.available -= quantity
        stock.reserved += quantity

        await self.session.flush() 
        await self.session.commit()
        await self.session.refresh(stock)
        return stock


    async def commit(self, product_id: int, quantity: int) -> Stock | None: 
        """Списывает quantity из reserved (после оплаты)."""
        stock = await self.get_for_update(product_id)

        if stock is None:
            return None

        if stock.available < quantity:
            return None

        stock.reserved -= quantity

        await self.session.flush() 
        await self.session.commit()
        await self.session.refresh(stock)
        return stock


    async def release(self, product_id: int, quantity: int) -> Stock | None: 
        """Возвращает quantity из reserved в available (компенсация)."""
        stock = await self.get_for_update(product_id)

        if stock is None:
            return None

        if stock.available < quantity:
            return None

        stock.reserved -= quantity
        stock.available += quantity

        await self.session.flush() 
        await self.session.commit()
        await self.session.refresh(stock)
        return stock


    