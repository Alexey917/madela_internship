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


    async def update(
            self, 
            product_id: int,
            price: Decimal,
            stock: int,
            name: str | None = None,
            is_active: bool | None = None,
            description: str | None = None,
            publisher: str | None = None,
            min_players: int | None = None,
            max_players: int | None = None,
            play_time_minutes: int | None = None,
            min_age: int | None = None,
    ) -> Product | None:
        product = await self.session.get(Product, product_id)

        if product is None:
            return None

        if name is not None:
            product.name = name

        if price is not None:
            product.price = price

        if stock is not None:
            product.stock = stock

        if is_active is not None:
            product.is_active = is_active

        if description is not None:
            product.description = description

        if publisher is not None:
            product.publisher = publisher

        if min_players is not None:
            product.min_players = min_players

        if max_players is not None:
            product.max_players = max_players

        if play_time_minutes is not None:
            product.play_time_minutes = play_time_minutes

        if min_age is not None:
            product.min_age = min_age

        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product
        
