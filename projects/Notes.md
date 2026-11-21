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

## Inventory Service

- [x] 10: **каркас + инфра**
  - [x] 10.1: Тоже самое что и в пункте 1 Catalog
  - [x] 10.2: Тоже самое что и в пункте 7 Catalog

- [x] 11: **модель + Alembic + sed**
  - [x] 11.1: Тоже самое что и в пункте 2 Catalog
  - [x] 11.2: Создание seed.py в папке scripts
  - [x] 11.3: Добавление запуска seed в entrypoint.sh: python -m scripts.seed
  - [x] 11.4: Проверка бд: docker exec -it projects-inventory-postgres-1 psql -U inventory -d inventory_db \
  -c "SELECT product_id, available, reserved FROM stock ORDER BY product_id;"

- [x] 12: **repository**
  - [x] 12.1: Тоже самое что и в пункте 3 Catalog
  - [x] 12.2: Сброс данных после теста: docker exec -it projects-inventory-postgres-1 psql -U inventory -d inventory_db \
  -c "UPDATE stock SET available=3, reserved=0 WHERE product_id=9;"

- [x] 13: **schemas + routers**
  - [x] 12.1: Тоже самое что и в пункте 4 Catalog
  - [x] 12.2: Проверка: получить stock по id, зарезервировать, зарезервировать больше чем есть, зарезервировать не существующий, конпенсация, потверждение, зарезервировать с количеством 0
  - [x] 12.3: Сброс данных после теста: docker exec -it projects-inventory-postgres-1 psql -U inventory -d inventory_db \
  -c "UPDATE stock SET available=3, reserved=0 WHERE product_id=9;"

 - [x] 14: **idempotency_key + cache**
  - [x] 14.1: Создание cache.py
  - [x] 14.2: Закрытие клиента в main.py await redis_client.aclose()
  - [x] 14.3: Создание idempotency.py с функцией проверки ключа в заголовке, функцией закешированного ответа и функцией сохранения ответа с TTL 24ч
  - [x] 14.4: В мутирующий эндпоинтах сначало проверяем есть ли ключ в заголовке ответа
  - [x] 14.5: Возвращаем закешированный ответ если он есть, если нет возвращаем JSONResponse со статусом и телом
  - [x] 14.5: Если ответа нет получаем его как обычно из бд, а затем сохраняем в кеш, как при ошибках, так и при успехе
  - [x] 14.6: Пересобрать докер docker compose up -d --build inventory
  - [x] 14.7: Проверка успешное резервирование с повтором, ошибка с повтором, отсутствие ключа, новый ключ
  - [x] 14.8: Проверка Redis docker exec -it projects-inventory-redis-1 redis-cli KEYS "idem:*"
  - [x] 14.9: Проверка TTL docker exec -it projects-inventory-redis-1 redis-cli TTL "idem:test-key-1"
  - [x] 14.10: Сброс данных docker exec -it shop-inventory-postgres-1 psql -U inventory -d inventory_db \
  -c "UPDATE stock SET available=3, reserved=0 WHERE product_id=9;" docker exec -it shop-inventory-redis-1 redis-cli DEL idem:test-key-1 idem:test-key-2 idem:test-key-3

- [x] 15: **RabbitMQ + Outbox**
  - [x] 15.1: Тоже самое что и в пункте 9 Catalog
  - [x] 15.2: Проверка: успешный reserve - проверка outbox, reserve failed (нехватка) - проверка outbox, release - проверка outbox
  - [x] 15.3: Проверка outbox docker exec -it projects-inventory-postgres-1 psql -U inventory -d inventory_db \
  -c "SELECT id, event_type, payload, published_at FROM outbox_messages ORDER BY id DESC LIMIT 3;"
  - [x] 15.4: Сброс: docker exec -it projects-inventory-postgres-1 psql -U inventory -d inventory_db \
  -c "UPDATE stock SET available=3, reserved=0 WHERE product_id=9;" docker exec -it projects-redis-1 redis-cli FLUSHDB

- [x] 16: **Consumer для inventory.reserve**
  - [x] 16.1: Создание consumer.py
  - [x] 16.2: start_consumer будет запускать consumer 
    - [x] 16.2.1: Сначала проверка на существование канала 
    - [x] 16.2.2: Cоздание собственного обменника для inventory.reserve
    - [x] 16.2.3: Cозадание очереди 
    - [x] 16.2.4: Привязка к очереди по обменнику и routing_key 
    - [x] 16.2.5: Перебор элементов из очереди с автоматическим подтверждением message.process()
  - [x] 16.3: обработчик _handle_inventory_reserve будет осуществлять бизнес логику
    - [x] 16.3.1: Из тела сообщения достаем id заказа и массив товаров, если чего-то из этого нет, выходим из функции
    - [x] 16.3.2: Если есть id и массив, создаем сессию - перебираем массив и резервируем каждый товар, если товара не существует, то возвращаем все что было зарезервировано в исходное состояние(делаем release)
    - [x] 16.3.3: Сохраняем в бд событие и данные(добавляем id заказа) как при ошибке так и при успехе
    - [x] 16.3.4: При существовании stock добавляем его в массив зарезервированных товаров
  - [x] 16.4: функция _publish фиксирует событие и данные в outbox
  - [x] 16.5: В lifespan создается такса с consumer, ожидается, отменяется
  - [x] 16.6: Проверка 
    - [x] 16.6.1: При старте контейнера должен быть виден лог о старте consumer
    - [x] 16.6.2: В http://localhost:15672 → Exchanges → order.events сделать публикацию сообщения с ключом inventory.reserve и "успешными данными", проверить логи сервиса, проверить запись в outbox таблице
    - [x] 16.6.3: Аналогично проверить "провальный резерв" 
    - [x] 16.6.4: Аналогично проверить "частично провальный резерв"
    - [x] 16.6.5: Сбросить данные

## Payment Service

- [x] 17: **Каркас + инфра**
  - [x] 17.1: Тоже что и в 10 пункте (Inventory)

- [x] 18: **модель + Alembic**
  - [x] 18.1: Тоже самое что и в пункте 2 Catalog
  - [x] 18.2: Т.к порты не через localhost, то миграцию нужно сделать иначе docker compose exec payment alembic revision --autogenerate -m "create payments table" - если порт у бд не через localhost. В докере будет, в папке не будет
  - [x] 18.3: Скопировать файл миграции из контейнера на хост(в папку): docker compose cp payment:/app/alembic/versions/6c68263af20f_create_payments_table.py ./alembic/versions/
  - [x] 18.4: docker compose exec payment alembic upgrade head создать миграцию

- [x] 19: **Mock-шлюз + tenacity**
  - [x] 19.1: Добавление зависимости: poetry add tenacity httpx
  - [x] 19.2: Создание Mock-шлюза в mock_gateway.py(по сути эндпоинт, который эмулирует ответ платежной системы, выдавая ответы по алгоритму)
  - [x] 19.3 gateway_client.py вызывает шлюз с retry
  - [x] 19.4 Подключение Mock-шлюза в main.py app.include_router(mock_gateway_router)
  - [x] 19.5 Создание scripts/test_gateway.py для проверки Mock-шлюза с retry
  - [x] 19.6 Проверка poetry run python -m scripts.test_gateway

- [x] 20: **Схемы, репозиторий, роуты**
  - [x] 20.1: Добавление схем для данных на вход и выход ответа
  - [x] 20.2: Добавление репозитория с crud-операциями и создание репозитория как зависимости
  - [x] 20.3: Создание idempotency.py с функцией проверки ключа в заголовке, функцией закешированного ответа и функцией сохранения ответа с TTL 24ч
  - [x] 20.4: Создание эндпоинтов в routers/payments.py
  - [x] 20.5: В мутирующий эндпоинтах сначало проверяем есть ли ключ в заголовке ответа
  - [x] 20.6: Возвращаем закешированный ответ если он есть
  - [x] 20.7: Если ответа нет получаем его как обычно из бд, а затем сохраняем в кеш, как при ошибках, так и при успехе
  - [x] 20.8: В main.py подключаем роуты
  - [x] 20.9: Проверка
    - [x] 20.9.1: Пересборка докера docker compose up -d --build payment и проверка логов docker compose logs payment | tail -20
    - [x] 20.9.2: Создать платеж
    - [x] 20.9.3: Повторное создание платежа с тем же ключом(ответ должен быть из redis)
    - [x] 20.9.4: Повторное создание платежа с другим ключом(тот же id)
    - [x] 20.9.5: Запрос на refund
    - [x] 20.9.6: Повторный refund
    - [x] 20.9.7: Запрос без ключа
    - [x] 20.9.8: Сброс тестов docker exec -it projects-payment-postgres-1 psql -U payment -d payments_db -c "TRUNCATE payments RESTART IDENTITY;" docker compose exec redis redis-cli -n 2 FLUSHDB

- [x] 21: **broker + outbox + webhook**
  - [x] 21.1: Тоже что и в пункте 9 catalog
  - [x] 21.2: Создание эндпоинта для webhook
  - [x] 21.3: Проверка
    - [x] 21.3.1: Пересборка докера docker compose up -d --build payment и проверка логов docker compose logs payment | tail -20
    - [x] 21.3.2: Создать усешный платеж
    - [x] 21.3.3: Проверка outbox docker exec -it projects-payment-postgres-1 psql -U payment -d payments_db \
  -c "SELECT id, event_type, published_at FROM outbox_messages ORDER BY id DESC LIMIT 5;"
    - [x] 21.3.3: Создать refund
    - [x] 21.3.4: Проверка outbox 
    - [x] 21.3.5: Сброс теста docker exec -it shop-payment-postgres-1 psql -U payment -d payments_db -c " TRUNCATE payments RESTART IDENTITY; TRUNCATE outbox_messages RESTART IDENTITY;" docker compose exec redis redis-cli -n 2 FLUSHDB

- [x] 22: Consumer для order.created
  - [x] 22.1: Создание consumer.py
  - [x] 22.2: start_consumer будет запускать consumer
    - [x] 22.2.1: Сначала проверка на существование канала
    - [x] 22.2.2: Cоздание собственного обменника для order.created
    - [x] 22.2.3: Cозадание очереди
    - [x] 22.2.4: Привязка к очереди по обменнику и routing_key
    - [x] 22.2.5: Перебор элементов из очереди с автоматическим подтверждением message.process()
  - [x] 22.3: обработчик _handle_order_created будет осуществлять бизнес логику
    - [x] 22.3.1: Из тела сообщения достаем id заказа и сумму, если чего-то из этого нет, выходим из функции
    - [x] 22.3.2: Если есть id и сумма, создаем сессию - и вызываем await repo.create_and_charge(order_id, amount)
  - [x] 22.4: В lifespan создается такса с consumer, ожидается, отменяется
  - [x] 22.5: Проверка
    - [x] 22.5.1: Пересборка + логи docker compose up -d --build payment docker compose logs -f payment
    - [x] 22.5.2: В http://localhost:15672 → Exchanges → order.events сделать публикацию сообщения с ключом order.created и "успешными данными", проверить логи сервиса, проверить запись в outbox таблице и бд
    - [x] 22.5.3: Проверить идемпотентность опубликовать тот же order_id
    - [x] 22.5.4: Сброс данных docker exec -it shop-payment-postgres-1 psql -U payment -d payments_db -c " TRUNCATE payments RESTART IDENTITY; TRUNCATE outbox_messages RESTART IDENTITY;" docker compose exec redis redis-cli -n 2 FLUSHDB

## Order Service

- [x] 23: **Каркас + инфра**
  - [x]23.1: Тоже что и в 17 пункте (Payment)

- [x] 24: **Модель + миграция**
   - [x]24.1: Создание моделей: заказы, состояние саги, айтемы заказа, аутбокс
   - [x]24.2: Миграции poetry run alembic revision --autogenerate -m "create orders, order_items, saga_state, outbox" poetry run alembic upgrade head
   - [x]24.3: проверка бд docker exec -it shop-order-postgres-1 psql -U order -d orders_db -c "\dt"

- [x] 25: **Репозиторий**
  - [x]25.1: Создание репозитория
  - [x]25.2: Скрипт для проверки poetry run python -m scripts.test_repo
  - [x]25.3: Проверка бд и сброс тестов  docker exec -it shop-order-postgres-1 psql -U order -d orders_db -c "SELECT id, user_id, status, total_amount FROM orders;SELECT id, order_id, product_id, quantity, unit_price FROM order_items;SELECT order_id, status, last_error FROM saga_state;" docker exec -it shop-order-postgres-1 psql -U order -d orders_db -c "TRUNCATE orders, order_items, saga_state RESTART IDENTITY CASCADE;"

- [x] 26: **broker + outbox**
  - [x] 26.1: Тоже что и пункт 9 каталога

- [x] 27: **saga**
  - [x] 27.1: Создание saga.py
  - [x] 27.2: Создание класса ServiceSaga 
    - [x] 27.2.1: Каждый метод будет получить заказ по id
    - [x] 27.2.2: Затем проверка если заказа нет, то метод выполнять не нужно, не забываем логировать
    - [x] 27.2.3: Затем проверка статуса заказа, если статус в терминальном(статус - процесс завершён, дальше двигаться некуда) состоянии, или уже обработан, то мы логируем и ничего не делаем(идемпотентность)
    - [x] 27.2.4: Затем обновляем статус саги и заказа, если это нужно
    - [x] 27.2.5: Затем публикуем необходимое событие 
    - [x] 27.2.6: Коммит в конце
  - [x] 27.3: Saga машина:
    - [x] 27.3.1: Публикуем inventory.reserve
    - [x] 27.3.2: Ждем inventory.reserved, если есть публикуем payment.process
    - [x] 27.3.3: Если получен inventory.failed, запускаем компенсацию, меняем статусы дважды(compensation->cancelled) т.к процесса покупки здесь еще нет и отменять ее не нужно
    - [x] 27.3.4: Если платеж прошел payment.succeeded, то запускаем payment.commit и делаем статусы в completed
    - [x] 27.3.5: Если платеж не прошел payment.failed, то запускаем компенсацию, публикуем inventory.release
    - [x] 27.3.6: Если получаем inventory.released, меняем статус на cancelled
  - [x] 27.4: Без роутов можно протестировать через скрипт poetry run python -m scripts.test_saga
  - [x] 27.5: После теста сбросить данные docker exec -it shop-order-postgres-1 psql -U order -d orders_db -c "TRUNCATE orders, order_items, saga_state, outbox_messages RESTART IDENTITY CASCADE;"docker exec -it shop-inventory-postgres-1 psql -U inventory -d inventory_db -c "UPDATE stock SET available=3, reserved=0 WHERE product_id=9;TRUNCATE outbox_messages RESTART IDENTITY;"

- [x] 28: **consumer + роуты**
  - [x] 28.1: Старт консьюмера для инвентори
    - [x] 28.1.1: Если канал отсутствует выбрасываем ошибку raise RuntimeError("Broker is not connected")
    - [x] 28.1.2: Создание обменника для inventory.events
    - [x] 28.1.3: Создание очереди
    - [x] 28.1.4: Привязка очереди к событиям inventory.reserved, inventory.failed, inventory.released
    - [x] 28.1.5: Перебираем сообщения из очереди и вызываем соответствующий обработчик
  - [x] 28.2: Аналогично для консьюмера payment
  - [x] 28.3: Обработчики достают из сообщения order_id, если он есть, то по routing_key вызывают соответствующий метод саги, иначе ничего не делаем и логируем
  - [x] 28.4: Создание схем
  - [x] 28.5: Создание роутов
  - [x] 28.6: Создание тасков для consumer в main.py
  - [x] 28.7: Протестировать удачный и не удачный сценарии покупки

## Notification Service

- [x] 29: ** Каркас + инфра**
  - [x] 29.1: Тоже что и в 23 пункте (Order)

- [x] 30: ** Модель + миграция**
  - [x] 30.1: Создание модели и создание миграции

- [x] 31: ** broker + Consumer на 4 события**
  - [x] 31.1: Создание broker упрощенный без обменника
  - [x] 32.2: Создание consumer 
  - [x] 32.3: Создание repository для создания уведомления и сохранения в бд

## Gateway Service

- [x] 32: **gateway**
  - [x] 32.1: Создание Dockerfile и добавление сервиса в compose
  - [x] 32.2: Создание nginx.conf

## UI Service

- [x] 33: **ui**
  - [x] 33.1: Установка сборщика и окружения npm create vite@latest . -- --template react-ts
  - [x] 34.2: Установка зависимостей npm install antd @ant-design/icons motion npm install -D @types/node
  - [x] 34.3: Создание ui

## Auth Service

- [x] 34: **auth**
  - [x] 34.1: Начинаем как обычно создаем сервисы с инфры
  - [x] 34.2: Добавляем зависимость poetry add "passlib[bcrypt]" python-jose
  - [x] 34.3: Создание модели пользователя
  - [x] 34.4: Миграции и seed пользователей
  - [x] 34.5: Создание pydantic схем
  - [x] 34.6: Создание security.py:
    - [x] 34.6.1: Создание контекста хеширования
    - [x] 34.6.2: Методы для хеширования пароля, "расхеширования", создание и кодирование токена, декодировка токена
  - [x] 34.7: Создание роутов для входа и для gateway






