# Development Notes

## Catalog Service

- [ ] 1: **каркас + инфра**
  - [ ] 1.1: Создание базовых файлов: .gitignore, Notes.md, README.md
  - [ ] 1.2: Папка для сервиса services/catalog
  - [ ] 1.3: Poetry + зависимости
  - [ ] 1.3: Создание переменных окружения
  - [ ] 1.4: Настройка postgres и redis в docker-compose.yml
  - [ ] 1.5: config.py для чтения значений из окружения и пустой __init__.py
  - [ ] 1.6: Создание приложения в main.py, подключение метрик и эндпоинт для проверки работоспособности
  - [ ] 1.7: Проверки:
    - [ ] 1.7.1 docker compose up -d 
    - [ ] 1.7.2 docker compose ps
    - [ ] 1.7.3 poetry run uvicorn app.main:app --reload --port 8001
    - [ ] 1.7.4 curl http://localhost:8001/health
    - [ ] 1.7.5 curl -s http://localhost:8001/metrics | head


- [ ] 2: **модель + Alembic**
  - [ ] 2.1: Создание db.py установка пулла соединений с бд и генератора сессий
  - [ ] 2.2: Создание models.py и описание базы данных
  - [ ] 2.2: Подключение alembic poetry run alembic init -t async alembic
  - [ ] 2.3: Закомментировать sqlalchemy.url = driver://user:pass@localhost/dbname в alembic.ini
  - [ ] 2.4: В env.py alembic'а импортируем настройки конфига, базовый класс из бд и модель
  - [ ] 2.5: config.set_main_option("sqlalchemy.url", settings.database_url)
  - [ ] 2.6: Установка метаданных модели target_metadata = Base.metadata
  - [ ] 2.7: Создание миграции poetry run alembic revision --autogenerate -m "create products table"(не забудь поднять докер)
  - [ ] 2.8: Применение миграции poetry run alembic upgrade head
  - [ ] 2.9: Проверка бд:
    - [ ] 2.9.1: docker exec -it shop-catalog-postgres-1 psql -U catalog -d catalog_db -c "\dt"
    - [ ] 2.9.2: docker exec -it shop-catalog-postgres-1 psql -U catalog -d catalog_db -c "\d products"
  - [ ] 2.10: Закрыть соединение с бд в lifespan при shutdown
  - [ ] 2.11: Проверка работоспособности


- [ ] 3: **repository**
  - [ ] 3.1: Создание repository.py и класса ProductRepositoty для описания методов list, get, create, update
  - [ ] 3.2: Создание scripts/test_repo.py (предварительно создать __init__.py и запустить docker) для проверки работы методов
  - [ ] 3.3: poetry run python -m scripts.test_repo для теста


- [ ] 4: схемы + роутеры
  - [ ] 4.1: Создание schemas.py и описание схем для списка продуктов, создания, обновления и получения получения по id
  - [ ] 4.2: Создание dependencies.py 
  - [ ] 4.3: Создание routes/products.py и написание роутов
  - [ ] 4.3: Подключение роутов в main.py app.include_router(products.router)
  - [ ] 4.4: Поднять докер, запустить poetry run uvicorn app.main:app --reload --port 8001
  - [ ] 4.5: Тестирование работоспособности
  - [ ] 4.6: Если есть ошибка в бд, то изменить поля через миграцию poetry run alembic revision -m "fix timestamp column names"
  - [ ] 4.6: В файле fix timestamp column names исправить поля и применить миграцию poetry run alembic upgrade head
  - [ ] 4.7: Сбросить не нужные записи в бд docker compose exec catalog-postgres psql -U catalog -d catalog_db -c "TRUNCATE TABLE products RESTART IDENTITY;"


- [ ] 5: кеш
  - [ ] 5.1: Создание cache.py 
  - [ ] 5.2: Закрытие клиента в main.py await redis_client.aclose()
  - [ ] 5.3: Создание get_cache в зависимостях
  создаем логгер
  - [ ] 5.4: Устанавливаем динамический ключ для кеша при получении списка cache_key = f"tasks:page:{page}:size:{size}"
  - [ ] 5.5: Преобразуем в бинарный вид cached = await get_json(cache_key)
  - [ ] 5.6: Если кеш есть, то логируем и возвращаем данные из кеша
  - [ ] 5.7: Если нет кеша, логируем и сохраняем список в кеш
  - [ ] 5.8: в мутирующих запросах перед результатом сбрасываем кеш await delete_pattern("tasks:*")
  - [ ] 5.9: cache: Redis = Depends(get_cache) - соблюдаем DI-паттерн
  - [ ] 5.10: Запускаем сервис poetry run uvicorn app.main:app --reload --port 8000
  - [ ] 5.11: Проверяем кеш curl "http://localhost:8000/tasks?page=1&size=10" в логах CACHE MISS: tasks:page:1:size:10.
  - [ ] 5.12: Проверяем кеш curl "http://localhost:8000/tasks?page=1&size:10" в логах CACHE HIT: tasks:page:1:size:10.
  - [ ] 5.13: Проверка redis на прямую docker exec -it todo-service-redis-1 redis-cli KEYS "tasks:*"
  - [ ] 5.14: Проверка ttl docker exec -it todo-service-redis-1 redis-cli TTL "tasks:page:1:size:10"
  - [ ] 5.15: Замеры скоростей time curl "http://localhost:8000/tasks?page=1&size=10" # MISS time curl "http://localhost:8000/tasks?page=1&size=10" # HIT

- [ ] 6: seed
  - [ ] 6.1: Создание seed.py в scripts
  - [ ] 6.2: Поднятие докера: docker compose up -d
  - [ ] 6.3: Запуск скрипта: poetry run python -m scripts.seed
  - [ ] 6.4: Проверка бд: docker exec -it shop-catalog-postgres-1 psql -U catalog -d catalog_db \
  -c "SELECT id, name, price, stock FROM products ORDER BY id;"

- [ ] 7: Dockerfile
- [ ] 8: README + проверка