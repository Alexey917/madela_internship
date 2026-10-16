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
27. создаем в папке app файл repository.py там будем писать все наши операции по получению данных с бд
28. пишем перации по получению данных с бд
29. создаем scripts/test_repo.py пока нет сервиса для проверки работы с будем
30. перед проверкой scripts/test_repo.py нужно запустить докер
31. создаем в app файлы dependencies.py и schemas.py, затем папку routers и в ней __init__.py и tasks.py
32. Пишем схемы
33. Создаем репо в dependencies кнему будем обращаться за методами для будем
34. пишем роуты
35. подключить роуты в main.py app.include_router(tasks.router)
36. запускаем poetry run uvicorn app.main:app --reload --port 8000 и докер не забудь поднять
37. тест на создание curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Купить хлеб", "description": "Не забыть"}'
38. тест на получение данных curl "http://localhost:8000/tasks?page=1&size=10"
39. тест получить по id curl http://localhost:8000/tasks/1
40. тест обновление curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"is_done": true}'
41. тест удаление curl -X DELETE http://localhost:8000/tasks/1
42. создаем cashe.py и в нем устанавливаем клиент, получение и установка данных, также удаление ключей
43. в main.py закрыть клиент в lifespan await redis_client.aclose()
44. в dependecies возвращаем клиент через синхронный метод get_cache()
45. импортируем редис в роуты
46. создаем логгер
47. устанавливаем динамический ключ для кеша при получении списка cache_key = f"tasks:page:{page}:size:{size}"
48. преобразуем в бинарный вид cached = await get_json(cache_key)
49. если кеш есть, то логируем и возвращаем данные из кеша
50. если нет кеша, логируем и сохраняем список в кеш
51. логи для демонстрации, в реальном проекте метрики
52. в мутирующих запросах перед результатом сбрасываем кеш await delete_pattern("tasks:*")
53. cache: Redis = Depends(get_cache) - соблюдаем DI-паттерн
54. запускаем сервис poetry run uvicorn app.main:app --reload --port 8000
55. проверяем кеш curl "http://localhost:8000/tasks?page=1&size=10" в логах CACHE MISS: tasks:page:1:size:10.
56. проверяем кеш curl "http://localhost:8000/tasks?page=1&size:10" в логах CACHE HIT: tasks:page:1:size:10.
57. проверка redis на прямую docker exec -it todo-service-redis-1 redis-cli KEYS "tasks:*"
58. проверка ttl docker exec -it todo-service-redis-1 redis-cli TTL "tasks:page:1:size:10"
59. замеры скоростей time curl "http://localhost:8000/tasks?page=1&size=10"  # MISS time curl "http://localhost:8000/tasks?page=1&size=10"  # HIT
60. 