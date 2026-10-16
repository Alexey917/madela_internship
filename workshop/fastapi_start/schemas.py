from pydantic import BaseModel

class BookSchema(BaseModel):
    title: str
    author: str

class BookAddSchema(BookSchema):
    id: int


class LoginSchema(BaseModel):
    username: str
    password: str