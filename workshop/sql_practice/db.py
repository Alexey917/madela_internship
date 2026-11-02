import os
from sqlalchemy import text
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://shop_user:shop_password@localhost:5432/shop_db"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = async_sessionmaker(
  engine,
  class_=AsyncSession,
  expire_on_commit=False,
)

async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("""CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            age INTEGER CHECK (age > 0),
            balance NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
            created_at TIMESTAMP DEFAULT NOW() 
        )"""))
    
        await conn.execute(text("""CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
            description VARCHAR(1000),
            rate NUMERIC(10, 1) NOT NULL CHECK (rate > 0 AND rate < 5),
            quantity INTEGER DEFAULT 0 CHECK (quantity >= 0),
            created_at TIMESTAMP DEFAULT NOW()
        )"""))
    
        await conn.execute(text("""CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users (id),
            created_at TIMESTAMP DEFAULT NOW() 
        )"""))
    
        await conn.execute(text("""CREATE TABLE IF NOT EXISTS order_item (
            id SERIAL PRIMARY KEY,
            price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
            order_id INTEGER NOT NULL REFERENCES orders(id),
            product_id INTEGER NOT NULL REFERENCES products(id)
        )"""))


async def insert_data() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE order_item, orders, products, users RESTART IDENTITY CASCADE"))

        await conn.execute(text("""
            INSERT INTO users (name, email, age, balance) VALUES
                ('Алексей Иванов', 'alexey@example.com', 28, 1500.00),
                ('Мария Петрова', 'maria@example.com', 34, 2300.50),
                ('Дмитрий Сидоров', 'dmitry@example.com', 22, 0.00),
                ('Елена Козлова', 'elena@example.com', 41, 540.75),
                ('Иван Смирнов', 'ivan@example.com', 19, 120.00),
                ('Ольга Морозова', 'olga@example.com', 30, 8900.00),
                ('Сергей Волков', 'sergey@example.com', 25, 300.00),
                ('Анна Соколова', 'anna@example.com', 37, 45.20),
                ('Павел Лебедев', 'pavel@example.com', 45, 0.00),
                ('Татьяна Новикова', 'tatiana@example.com', 29, 670.10);
        """))