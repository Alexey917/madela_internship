from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select
from typing import Annotated
from pydantic import BaseModel

from fastapi import FastAPI, Depends

engine = create_async_engine('sqlite+aiosqlite:///books.db')  # создали бд books.db

app = FastAPI()

new_session = async_sessionmaker(engine, expire_on_commit=False)  # создали сессию - она по своей сути является транзакцией в sql

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Base(DeclarativeBase):
    pass


class BookModel(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str] 


class BookSchema(BaseModel):
    title: str
    author: str

class BookAddSchema(BookSchema):
    id: int



@app.post("/setup_database")  # обычно так не делают, это чисто для примера
async def setup_database():
    # открываем соединение с бд
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # drop_all очистит полностью бд
        await conn.run_sync(
            Base.metadata.create_all)  # Base.metadata хранятся все данные о все таблицах, create_all создает все таблицы, все столбцы
        return {"ok": True}


@app.post("/books")
async def add_book(data: BookAddSchema, session: SessionDep):
    new_book = BookModel(
        title=data.title,
        author=data.author,
    )

    session.add(new_book)
    await session.commit()  # отправка данных в бд
    return {"ok": True}


@app.get("/books")
async def get_books(session: SessionDep):
    query = select(BookModel)
    result = await session.execute(query)  # исполни код query
    return result.scalars().all()  # result это итератор