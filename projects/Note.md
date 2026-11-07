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



  

