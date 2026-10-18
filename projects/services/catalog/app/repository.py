from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models import Product


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def list(self, page: int = 1, size: int = 20, only_active: bool = True) -> tuple[list[Product], int]:
        offset = (page - 1) * size

        base_filter = Product.is_active.is_(True) if only_active else None

        query_count = select(func.count()).select_from(Product)

        if base_filter is not None:
            query_count = query_count.where(base_filter)

        total_count = await self.session.execute(query_count)
        total = total_count.scalar_one()

        query = select(Product).order_by(Product.id).offset(offset).limit(size)

        if base_filter is not None:
            query = query.where(base_filter)

        result = await self.session.execute(query)
        products =  list(result.scalars().all())

        return products, total


    async def get(self, product_id: int, only_active: bool = True) -> Product | None:
        query = select(Product).where(Product.id == product_id)

        if only_active:
            query = query.where(Product.is_active.is_(True))
        product = await self.session.execute(query)

        return product.scalar_one_or_none()


    async def create(
        self, 
        name: str,
        price: Decimal,
        stock: int,
        description: str | None = None,
        publisher: str | None = None,
        min_players: int | None = None,
        max_players: int | None = None,
        play_time_minutes: int | None = None,
        min_age: int | None = None,
    ) -> Product:
        product = Product(
            name = name,
            description = description,
            publisher = publisher,
            min_players = min_players,
            max_players = max_players,
            play_time_minutes = play_time_minutes,
            min_age = min_age,
            price = price,
            stock = stock
        )

        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product
