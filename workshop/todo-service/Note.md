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
14. docker compose up -d
15. docker compose ps - проверка всех поднятых сервисов
16. создаем db.py для настройки бд
17. создаем models.py для таблиц
18. poetry run alembic init -t async alembic создаем алембик для миграций
19. в файле alembic.ini прописываем работу alembic
20. poetry run alembic revision --autogenerate -m "create tasks table" создаем миграциюб должна появится версия с описанием, а не пустой файл
21. poetry run alembic upgrade head применяем миграцию
22. docker exec -it todo-service-postgres-1 psql -U todo -d todo_db -c "\dt"  проверка таблиц
23. docker exec -it todo-service-postgres-1 psql -U todo -d todo_db -c "\dt"  проверка конкретной таблицы
24. добавляем подключение бд в main.py и прописываем lifespan
25. poetry run uvicorn app.main:app --reload --port 8000 проверяем работу
26. проверяем health check -  curl http://localhost:8000/health