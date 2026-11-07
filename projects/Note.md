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


