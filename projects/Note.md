- [x] 23: **Каркас + инфра**
  - [x]23.1: Тоже что и в 17 пункте (Payment)

- [x] 24: **Модель + миграция**
   - [x]24.1: Создание моделей: заказы, состояние саги, айтемы заказа, аутбокс
   - [x]24.2: Миграции poetry run alembic revision --autogenerate -m "create orders, order_items, saga_state, outbox" poetry run alembic upgrade head
   - [x]24.3: проверка бд docker exec -it shop-order-postgres-1 psql -U order -d orders_db -c "\dt"