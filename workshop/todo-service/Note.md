1. Создаем папку
2. Создаем гитигнор:
3. Устанавливаем poetry:  (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
4. Инициализируем проект: poetry init --no-interaction --name todo-service --python "^3.12"
5. Устанавливаем зависимости: poetry add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" asyncpg alembic pydantic-settings redis prometheus-fastapi-instrumentator
6. устанавливаем: poetry add --group dev ruff black mypy
7. создаем .env.example и помещаем туда переменные
8. создаем .env и cp .env.example .env
9. создаем докер компоуз для бд и редис
10. создаем папку app
11. в app пустой __init__.py
12. создаем config.py и описываем настройки для переменных окружения
13. создаем main.py создаем приложение и эндпоинт для проверки