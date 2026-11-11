import asyncio

from decimal import Decimal
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Product

SEED_PRODUCTS = [
  {
    "name": "Каркассон",
    "publisher": "Hobby World",
    "min_players": 2,
    "max_players": 5,
    "play_time_minutes": 45,
    "min_age": 8,
    "price": Decimal("2990.00"),
    "stock": 15,
    "description": "Классическая игра о строительстве средневековых городов и дорог.",
  },
  {
    "name": "Catan",
    "publisher": "Hobby World",
    "min_players": 3,
    "max_players": 4,
    "play_time_minutes": 90,
    "min_age": 10,
    "price": Decimal("3490.00"),
    "stock": 20,
    "description": "Колонизация острова Катан: ресурсы, торговля, строительство.",
  },
  {
    "name": "Манчкин",
    "publisher": "Hobby World",
    "min_players": 3,
    "max_players": 6,
    "play_time_minutes": 60,
    "min_age": 12,
    "price": Decimal("1490.00"),
    "stock": 50,
    "description": "Пародийная карточная игра про подземелья и монстров.",
  },
  {
    "name": "Codenames",
    "publisher": "Стиль Жизни",
    "min_players": 2,
    "max_players": 8,
    "play_time_minutes": 15,
    "min_age": 14,
    "price": Decimal("1990.00"),
    "stock": 30,
    "description": "Командная игра на ассоциации и угадывание слов.",
  },
  {
    "name": "Билет на поезд",
    "publisher": "Hobby World",
    "min_players": 2,
    "max_players": 5,
    "play_time_minutes": 60,
    "min_age": 8,
    "price": Decimal("3990.00"),
    "stock": 10,
    "description": "Строительство железных дорог и выполнение маршрутов.",
  },
  {
    "name": "Диксит",
    "publisher": "Стиль Жизни",
    "min_players": 3,
    "max_players": 6,
    "play_time_minutes": 30,
    "min_age": 8,
    "price": Decimal("2490.00"),
    "stock": 25,
    "description": "Игра на воображение с ассоциативными картами.",
  },
  {
    "name": "7 Wonders",
    "publisher": "Стиль Жизни",
    "min_players": 3,
    "max_players": 7,
    "play_time_minutes": 30,
    "min_age": 10,
    "price": Decimal("4490.00"),
    "stock": 12,
    "description": "Развитие цивилизаций и строительство чудес света.",
  },
  {
    "name": "Splendor",
    "publisher": "Hobby World",
    "min_players": 2,
    "max_players": 4,
    "play_time_minutes": 30,
    "min_age": 10,
    "price": Decimal("3490.00"),
    "stock": 18,
    "description": "Торговля драгоценными камнями и развитие бизнеса.",
  },
  {
    "name": "Gloomhaven",
    "publisher": "Hobby World",
    "min_players": 1,
    "max_players": 4,
    "play_time_minutes": 120,
    "min_age": 14,
    "price": Decimal("12990.00"),
    "stock": 3,
    "description": "Кампанейская игра в жанре тактической RPG.",
  },
  {
    "name": "Azul",
    "publisher": "Стиль Жизни",
    "min_players": 2,
    "max_players": 4,
    "play_time_minutes": 45,
    "min_age": 8,
    "price": Decimal("3290.00"),
    "stock": 8,
    "description": "Абстрактная игра о выкладывании плиток.",
  },
  {
    "name": "Смертельные материалы",
    "description": "Помогите незнакомцам пройти ряд комнат с опасными испытаниями, избежать гибели и вспомнить, как все они между собой связаны. Это карточный квест-детектив с логическими и дедуктивными загадками, атмосферой хоррора и необычной механикой.",
    "publisher": "HOBBY WORLD",
    "min_players": 1,
    "max_players": 6,
    "play_time_minutes": 30,
    "min_age": 18,
    "stock": 14,
    "price": 500
  },
  {
    "name": "Морской бой",
    "description": "Перед Вами увлекательная настольная игра – «Морской бой». В нее можно играть снова и снова! Ведь в наборе есть все необходимое для победы над соперником. Играйте дома и в дороге, ведь магнитные фишки крепко держатся на металлическом поле. А еще их так удобно хранить в жестяной коробочке!",
    "publisher": "Десятое королевство",
    "min_players": 2,
    "max_players": 15,
    "play_time_minutes": 15,
    "min_age": 5,
    "stock": 7,
    "price": 500
  }
]


async def seed() -> None:
    async with SessionLocal() as session:
        created = 0
        skipped = 0

        for product in SEED_PRODUCTS:
            existing = await session.execute(select(Product.id).where(Product.name == product["name"]).limit(1))

            if existing.scalar_one_or_none() is not None:
                skipped += 1
                continue

            session.add(Product(**product))
            created += 1

        await session.commit()

    print(f"✅ Seed done: created={created}, skipped={skipped}")


if __name__ == "__main__":
    asyncio.run(seed())

            