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

- [x] 16: **Consumer для order.created**
  - [x] 16.1: Создание consumer.py
  - [x] 16.2: start_consumer будет запускать consumer 
    - [x] 16.2.1: Сначала проверка на существование канала 
    - [x] 16.2.2: Cоздание собственного обменника для order.created
    - [x] 16.2.3: Cозадание очереди 
    - [x] 16.2.4: Привязка к очереди по обменнику и routing_key 
    - [x] 16.2.5: Перебор элементов из очереди с автоматическим подтверждением message.process()
  - [x] 16.3: обработчик _handle_order_created будет осуществлять бизнес логику
    - [x] 16.3.1: Из тела сообщения достаем id заказа и массив товаров, если чего-то из этого нет, выходим из функции
    - [x] 16.3.2: Если есть id и массив, создаем сессию - перебираем массив и резервируем каждый товар, если товара не существует, то возвращаем все что было зарезервировано в исходное состояние(делаем release)
    - [x] 16.3.3: Сохраняем в бд событие и данные(добавляем id заказа) как при ошибке так и при успехе
    - [x] 16.3.4: При существовании stock добавляем его в массив зарезервированных товаров
  - [x] 16.4: функция _publish фиксирует событие и данные в outbox
  - [x] 16.5: В lifespan создается такса с consumer, ожидается, отменяется
  - [x] 16.6: Проверка 
    - [x] 16.6.1: При старте контейнера должен быть виден лог о старте consumer
    - [x] 16.6.2: В http://localhost:15672 → Exchanges → order.events сделать публикацию сообщения с ключом order.created и "успешными данными", проверить логи сервиса, проверить запись в outbox таблице
    - [x] 16.6.3: Аналогично проверить "провальный резерв" 
    - [x] 16.6.4: Аналогично проверить "частично провальный резерв"
    - [x] 16.6.5: Сбросить данные




