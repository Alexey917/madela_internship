from pydantic import BaseModel, Field, field_validator, ValidationError
import sys, re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8') 

class LoginSchema(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)

    @field_validator('password', mode="after")
    def check_password(cls, value):
        if re.fullmatch(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^a-zA-Z0-9]).+$', value):
            return value
        else:
            raise ValueError('Пароль должен содержать хотя бы одну цифру, строчную букву, заглавную букву и спец символ')
        

def login(schema: LoginSchema):
    return schema.username, schema.password


my_username = input('Введите логин:')
my_password = input('Введите пароль:')

try:
    data = LoginSchema(username=my_username, password=my_password)
    print(login(data))
except ValidationError as e:
    for err in e.errors():
        print(f"Поле: {err['loc']}, ошибка: {err['msg']}")


