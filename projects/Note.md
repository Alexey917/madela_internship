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






