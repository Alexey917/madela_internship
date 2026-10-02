from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from sqlalchemy import select
from typing import Annotated
from authx import AuthX, AuthXConfig

from schemas import BookSchema, BookAddSchema, LoginSchema
from models import Base, BookModel

from fastapi import FastAPI, Depends, HTTPException, Response

config = AuthXConfig()
config.JWT_SECRET_KEY = 'SECRET_KEY' # секретный ключ
config.JWT_ACCESS_COOKIE_NAME = "my_access_token" # имя токена
config.JWT_TOKEN_LOCATION = ["cookies"]  # как хранить токен

security = AuthX(config=config)

engine = create_async_engine('sqlite+aiosqlite:///books.db')  # создали бд books.db

app = FastAPI()

new_session = async_sessionmaker(engine, expire_on_commit=False)  # создали сессию - она по своей сути является транзакцией в sql

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


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


@app.post("/login")
def login(creds: LoginSchema, response: Response):
    if creds.username == 'test' and creds.password == 'test':
        token = security.create_access_token(uid="12345")
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token) # response - наш ответ фронту, т.е в ответе устанавливаем токен в куки и передаем с запросом
        return { "access_token": token }
    raise HTTPException(status_code=401, detail="Incorrect username or password")


@app.get("/protected", dependencies=[Depends(security.access_token_required)]) # тут еще 500 ошибка в случае отсутствия кук, а должна быть 403
def protected():
    return { "data": "TOP Secret" }