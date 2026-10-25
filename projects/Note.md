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
 

