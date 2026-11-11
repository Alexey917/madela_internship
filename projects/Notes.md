# Development Notes

## Catalog Service

- [x] 1: **каркас + инфра**
  - [x] 1.1: Создание базовых файлов: .gitignore, Notes.md, README.md
  - [x] 1.2: Папка для сервиса services/catalog
  - [x] 1.3: Poetry + зависимости
  - [x] 1.3: Создание переменных окружения
  - [x] 1.4: Настройка postgres и redis в docker-compose.yml
  - [x] 1.5: config.py для чтения значений из окружения и пустой __init__.py
  - [x] 1.6: Создание приложения в main.py, подключение метрик и эндпоинт для проверки работоспособности
  - [x] 1.7: Проверки:
    - [x] 1.7.1 docker compose up -d 
    - [x] 1.7.2 docker compose ps
    - [x] 1.7.3 poetry run uvicorn app.main:app --reload --port 8001
    - [x] 1.7.4 curl http://localhost:8001/health
    - [x] 1.7.5 curl -s http://localhost:8001/metrics | head


- [x] 2: **модель + Alembic**
  - [x] 2.1: Создание db.py установка пулла соединений с бд и генератора сессий
  - [x] 2.2: Создание models.py и описание базы данных
  - [x] 2.2: Подключение alembic poetry run alembic init -t async alembic
  - [x] 2.3: Закомментировать sqlalchemy.url = driver://user:pass@localhost/dbname в alembic.ini
  - [x] 2.4: В env.py alembic'а импортируем настройки конфига, базовый класс из бд и модель
  - [x] 2.5: config.set_main_option("sqlalchemy.url", settings.database_url)
  - [x] 2.6: Установка метаданных модели target_metadata = Base.metadata
  - [x] 2.7: Создание миграции poetry run alembic revision --autogenerate -m "create products table"(не забудь поднять докер)
  - [x] 2.8: Применение миграции poetry run alembic upgrade head
  - [x] 2.9: Проверка бд:
    - [x] 2.9.1: docker exec -it shop-catalog-postgres-1 psql -U catalog -d catalog_db -c "\dt"
    - [x] 2.9.2: docker exec -it shop-catalog-postgres-1 psql -U catalog -d catalog_db -c "\d products"
  - [x] 2.10: Закрыть соединение с бд в lifespan при shutdown
  - [x] 2.11: Проверка работоспособности


- [x] 3: **repository**
  - [x] 3.1: Создание repository.py и класса ProductRepositoty для описания методов list, get, create, update
  - [x] 3.2: Создание scripts/test_repo.py (предварительно создать __init__.py и запустить docker) для проверки работы методов
  - [x] 3.3: poetry run python -m scripts.test_repo для теста


- [x] 4: схемы + роутеры
  - [x] 4.1: Создание schemas.py и описание схем для списка продуктов, создания, обновления и получения получения по id
  - [x] 4.2: Создание dependencies.py 
  - [x] 4.3: Создание routes/products.py и написание роутов
  - [x] 4.3: Подключение роутов в main.py app.include_router(products.router)
  - [x] 4.4: Поднять докер, запустить poetry run uvicorn app.main:app --reload --port 8001
  - [x] 4.5: Тестирование работоспособности
  - [x] 4.6: Если есть ошибка в бд, то изменить поля через миграцию poetry run alembic revision -m "fix timestamp column names"
  - [x] 4.6: В файле fix timestamp column names исправить поля и применить миграцию poetry run alembic upgrade head
  - [x] 4.7: Сбросить не нужные записи в бд docker compose exec catalog-postgres psql -U catalog -d catalog_db -c "TRUNCATE TABLE products RESTART IDENTITY;"


- [x] 5: кеш
  - [x] 5.1: Создание cache.py 
  - [x] 5.2: Закрытие клиента в main.py await redis_client.aclose()
  - [x] 5.3: Создание get_cache в зависимостях
  создаем логгер
  - [x] 5.4: Устанавливаем динамический ключ для кеша при получении списка cache_key = f"tasks:page:{page}:size:{size}"
  - [x] 5.5: Преобразуем в бинарный вид cached = await get_json(cache_key)
  - [x] 5.6: Если кеш есть, то логируем и возвращаем данные из кеша
  - [x] 5.7: Если нет кеша, логируем и сохраняем список в кеш
  - [x] 5.8: в мутирующих запросах перед результатом сбрасываем кеш await delete_pattern("tasks:*")
  - [x] 5.9: cache: Redis = Depends(get_cache) - соблюдаем DI-паттерн
  - [x] 5.10: Запускаем сервис poetry run uvicorn app.main:app --reload --port 8000
  - [x] 5.11: Проверяем кеш curl "http://localhost:8000/tasks?page=1&size=10" в логах CACHE MISS: tasks:page:1:size:10.
  - [x] 5.12: Проверяем кеш curl "http://localhost:8000/tasks?page=1&size:10" в логах CACHE HIT: tasks:page:1:size:10.
  - [x] 5.13: Проверка redis на прямую docker exec -it todo-service-redis-1 redis-cli KEYS "tasks:*"
  - [x] 5.14: Проверка ttl docker exec -it todo-service-redis-1 redis-cli TTL "tasks:page:1:size:10"
  - [x] 5.15: Замеры скоростей time curl "http://localhost:8000/tasks?page=1&size=10" # MISS time curl "http://localhost:8000/tasks?page=1&size=10" # HIT

- [x] 6: seed
  - [x] 6.1: Создание seed.py в scripts
  - [x] 6.2: Поднятие докера: docker compose up -d
  - [x] 6.3: Запуск скрипта: poetry run python -m scripts.seed
  - [x] 6.4: Проверка бд: docker exec -it shop-catalog-postgres-1 psql -U catalog -d catalog_db \
  -c "SELECT id, name, price, stock FROM products ORDER BY id;"

- [x] 7: Dockerfile
  - [x] 7.1: Создание .dockerignore
  - [x] 7.2: Создание Dockerfile
  - [x] 7.3: Создание entrypoint.sh
  - [x] 7.4: Добавление сервиса каталог в docker-compose.yml
  - [x] 7.5: Остановка старого образа docker compose down
  - [x] 7.6: Собрать образ каталога docker compose build catalog
  - [x] 7.7: Поднять все docker compose up -d, docker compose ps
  - [x] 7.8: Проверка логов docker compose logs catalog

- [x] 8: README + проверка
- [ ] 9: RabbitMQ + Outbox
  - [ ] 9.1: Добавление сервиса RabbitMQ для каталог в docker-compose и не забыть указать что, каталог зависит от этого сервиса
  - [ ] 9.2: Добавление зависимости для работы с rabbitmq: poetry add aio-pika
  - [ ] 9.3: Добавление пути для rabbitmq: RABBITMQ_URL=amqp://catalog:catalog@localhost:5673/
  - [ ] 9.4: Добавление в config.py url для rabbitmq
  - [ ] 9.5: Создание borker.py, класс брокер с инициализацией соединения, канала и обменника, а также метода для открытия соединения, закрытия соединения и отправки сообщения в очередь по routing_key
  - [ ] 9.6: Открытие и закрытие соединения в lifespan 
  - [ ] 9.7: Создание таблицы для OutboxMessage
  - [ ] 9.8: Создание миграций: poetry run alembic revision --autogenerate -m "create outbox_messages table", poetry run alembic 
  upgrade head
  - [ ] 9.9: Проверка созданной таблицы docker exec -it shop-catalog-postgres-1 psql -U catalog -d catalog_db -c "\d outbox_messages"
  - [ ] 9.10: Создание outbox.py в нем через enqueue_event создаем сообщение о событии и добавляем в бд
  - [ ] 9.11: Обновление repository.py беред коммитом нужно выполнить функцию enqueue_event при создании и обновлении товара
  - [ ] 9.12: В outbox.py добавляем outbox_worker, который будет бесконечно брать неопубликованные сообщения и опубликовывать их
  - [ ] 9.13: В lifespan создать таску, для публикации сообщений в фоне
  - [ ] 9.14: Для проверки сделать действие, которое создает событие(создать товар), после чего в таблице OutboxMessage появиться дата публикации docker exec -it projects-catalog-postgres-1 psql -U catalog -d catalog_db \
  -c "SELECT id, event_type, published_at FROM outbox_messages ORDER BY id DESC LIMIT 5;"


## Следующее

- [ ] Inventory Service + RabbitMQ + Outbox
- [ ] Payment Service
- [ ] Order Service + SAGA
- [ ] Notification Service
- [ ] API Gateway
- [ ] UI
- [ ] Метрики / Grafana