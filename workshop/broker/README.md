# FastAPI API Gateway + Catalog + Saga Orders (event-driven via RabbitMQ)

Демо: gateway проксирует запросы к catalog (100 мок-товаров) и orders (оркестратор саги).
Транспорт для саги — **RabbitMQ** (topic exchange `shop`); синхронный HTTP сохранён как fallback.
HTML-магазин: каталог → корзина → покупка.

```
gateway/  :8000  -> отдаёт HTML + проксирует /api/products*, /api/orders*, /api/checkout
catalog/  :8002  -> 100 мок-товаров, потребляет order.*, публикует stock.*
orders/   :8001  -> оркестратор саги POST /orders/checkout (публикует order.*, потребляет stock.*)
rabbitmq/ :5672 (amqp), :15672 (веб-панель, guest/guest)
```

## Запуск

```bash
docker compose up --build
```

Откройте:
- Магазин: http://localhost:8000
- Здоровье gateway: http://localhost:8000/health
- Каталог: http://localhost:8000/api/products
- Заказы: http://localhost:8000/api/orders
- Веб-панель RabbitMQ: http://localhost:15672 (guest/guest) — обмен `shop`, очереди `catalog.order-events`, `orders.stock-events`
- Документация: http://localhost:8000/docs, http://localhost:8001/docs, http://localhost:8002/docs

Локальный запуск (нужен брокер, иначе сервисы переключатся на HTTP):

```bash
docker run -d --name rabbit -p 5672:5672 -p 15672:15672 rabbitmq:4-management-alpine
# t1 catalog
RABBITMQ_URL=amqp://guest:guest@localhost:5672/ uvicorn main:app --port 8002 --app-dir catalog
# t2 orders
CATALOG_URL=http://localhost:8002 RABBITMQ_URL=amqp://guest:guest@localhost:5672/ uvicorn main:app --port 8001 --app-dir orders
# t3 gateway
ORDERS_URL=http://localhost:8001 CATALOG_URL=http://localhost:8002 uvicorn main:app --port 8000 --app-dir gateway
```

Без RabbitMQ оба сервиса стартуют со статусом `"broker": "down"`, а checkout выполняется по прямому HTTP.

## Как брокер переносит события между сервисами

Оба сервиса общаются только через RabbitMQ: публикуют в topic exchange `shop`, а нужные события получают из своих очередей по маске routing key.

```mermaid
flowchart LR
    subgraph ORD["orders :8001"]
        O["оркестратор саги"]
    end

    subgraph CAT["catalog :8002"]
        C["резерв / подтверждение / отмена"]
    end

    EX[("RabbitMQ<br/>exchange: shop")]
    Q1[["catalog.order-events<br/>order.*"]]
    Q2[["orders.stock-events<br/>stock.*"]]

    O -->|"publish: order.created<br/>order.confirmed<br/>order.cancelled"| EX
    EX --> Q1
    Q1 -->|"consume"| C

    C -->|"publish: stock.reserved<br/>stock.rejected<br/>stock.confirmed<br/>stock.cancelled"| EX
    EX --> Q2
    Q2 -->|"consume"| O
```

Поток один и тот же в обе стороны: сервис публикует событие в exchange, exchange по маске кладёт его в очередь, сервис-потребитель забирает событие из очереди и отвечает новым событием — так шаг саги превращается в пару request/reply.

## Почему выбрана обработка событий, а не очередь задач

В проекте не очередь задач в стиле Celery («выполни функцию X»), а **событийная модель через topic exchange**. В сообщении лежит **факт прошедшего** (`order.created` — «заказ создан»), а не команда на выполнение (`reserve(order_id)`). Каждый потребитель сам решает, касается ли его событие, по маске routing key (`order.*`, `stock.*`).

Почему именно так:

1. **Сага — это реакция на факты, а не цепочка вызовов.** Каждый шаг порождает событие, и продолжение логики — это реакция на него: `order.created` → резерв → `stock.reserved` → платёж → `order.confirmed`. Оркестратор не дёргает каталог напрямую, он публикует факт и ждёт ответного факта. Компенсация (`order.cancelled`) — просто ещё одно событие, которое все участники обрабатывают так же, как и остальные.
2. **Многоподписка и лёгкое расширение.** На `order.*` могут подписать catalog и любой новый сервис (аналитика, уведомления, лог заказов) — продюсер об этом не узнаёт и не меняется. В очереди задач одна задача достаётся ровно одному исполнителю, и «слушателей» добавить нельзя без правок отправителя.
3. **Слабая связанность и устойчивость.** Очереди durable: пока catalog лежит, события копятся в `catalog.order-events`, а не теряются. Отправитель не проверяет, жив ли потребитель; при недоступности брокера оба сервиса мягко переключаются на HTTP-fallback, не ломая контракт.
4. **Request/reply собирается из событий.** Ответ коррелируется по `order_id` + стадии саги через map futures в orders — не нужна выделенная reply-очередь на каждый вызов, как в RPC поверх очереди задач.

Чем это отличается от очереди задач:

| | Очередь задач (Celery / work queue) | Здесь: события через topic exchange |
|---|---|---|
| Содержимое сообщения | команда: «выполни `reserve(...)`» | факт: «заказ #N создан» |
| Кто обрабатывает | ровно один воркер из очереди | все, кто подписался на маску `order.*` |
| Связанность | отправитель знает очередь/задачу и ждёт результата | отправитель публикует факт, реакции независимы |
| Следующий шаг | цепочка задач или оркестратор зовёт HTTP | продолжение — реакция нового события |
| Результат | результат возвращается вызывающему (RPC / result backend) | reply — тоже событие, коррелируется по `order_id` |
| Смысл записи | «сделать» (намерение) | «произошло» (история, которую видно в трассе саги) |

Очередь задач выбрали бы, если бы нужна была именно точечная работа по расписанию на одном исполнителе — фоновые задачи, тяжёлые вычисления, ретраи на уровне задачи. Здесь же шаги саги — доменные события нескольких независимых участников, поэтому событийная модель.

Издержки модели тоже стоит учитывать: request/reply поверх событий требует таймаутов (`SAGA_STEP_TIMEOUT`), сообщение без ожидающего потребителя отбрасывается (в orders — с предупреждением в логе), а outbox/идемпотентность в демо не реализованы.

## Сага поверх брокера (оркестрация, transport=events)

`POST /api/checkout {"customer","items":[{"product_id","qty"}]}`:

1. orders: создаёт заказ `PENDING` и публикует `order.created {order_id, customer, items}`
2. catalog (потребитель `catalog.order-events <- order.*`): резервирует товар → публикует `stock.reserved {order_id, reservation_id, items, total}` либо `stock.rejected {reason}`. Отказ (например, остаток 0 — у каждого 17-го товара) → заказ `FAILED`, прерывание, компенсация не нужна
3. orders (потребитель `orders.stock-events <- stock.*`): мок-платёж — отказ, если `customer=="fail"` или `total>3000` → публикует `order.cancelled` (**компенсация**), catalog восстанавливает остаток и публикует `stock.cancelled`, заказ `CANCELLED`
4. платёж прошёл → публикуется `order.confirmed`, catalog подтверждает и публикует `stock.confirmed` → заказ `CONFIRMED`

Каждый заказ хранит трассу `saga: [...]` и `transport: "broker" | "http-fallback"` — это видно в интерфейсе и в `GET /api/orders/{id}`.
Checkout поверх событий работает по принципу request/reply: orders публикует событие и ждёт коррелированный ответ `stock.*` (по умолчанию 10с, настраивается через `SAGA_STEP_TIMEOUT`).

Синхронные HTTP-эндпоинты (`POST /reserve`, `/confirm/{id}`, `/cancel/{id}`) сохранены как fallback/для отладки.

Тестирование:

```bash
curl localhost:8000/health  # orders_service.broker + catalog_service.broker должны быть "up"
curl localhost:8000/api/products | head -c 300
# успех (через брокер, в трассе саги будет broker)
curl -X POST localhost:8000/api/checkout -H 'Content-Type: application/json' \
  -d '{"customer":"dave","items":[{"product_id":1,"qty":1},{"product_id":2,"qty":2}]}'
# нет товара на складе -> 409 (у товара 17 остаток 0)
curl -X POST localhost:8000/api/checkout -H 'Content-Type: application/json' \
  -d '{"customer":"dave","items":[{"product_id":17,"qty":1}]}'
# отказ платежа -> 402 + компенсация (customer=fail)
curl -X POST localhost:8000/api/checkout -H 'Content-Type: application/json' \
  -d '{"customer":"fail","items":[{"product_id":1,"qty":1}]}'
# сброс остатков каталога
curl -X POST localhost:8000/api/catalog/reset
```

## Пользовательский кейс: проверка брокера через UI

Откройте магазин: **http://localhost:8000**. В шапке три индикатора — `gateway` / `catalog` / `orders` (обновляются каждые 15 секунд). Все три должны быть 🟢 зелёными. Важно: индикаторы показывают доступность **сервисов**, а не брокера — работают ли события, видно по трассе саги ниже.

### Кейс 1. Успешный checkout через RabbitMQ (главная проверка)

1. В карточке **Catalog** нажмите `+ Add` у любого товара (можно у нескольких).
2. В карточке **🧺 Bucket** в поле `customer` введите любое имя, кроме `fail` (например `dave`).
3. Нажмите синюю кнопку **«Buy bucket — pay by price → POST /api/checkout»**.
4. Появится сообщение `⏳ saga running: reserve → pay → confirm…`, затем зелёное **«✅ order #N CONFIRMED»** и трасса саги. Проверьте в ней строки (все должны быть зелёными):
   - `1. order N created PENDING ... (transport=broker: publish order.created)`
   - `2. RESERVE ok via broker: reservation ... (stock.reserved)`
   - `3. PAYMENT ok: ... -> publish order.confirmed`
   - `4. CONFIRM ok via broker: ... -> order CONFIRMED (stock.confirmed)`
5. В карточке **Orders** нажмите **↻** и разверните **«saga trace (N)»** у нового заказа — должна гореть зелёная плашка **CONFIRMED** и виден `reservation: ...`.
6. В **Catalog** нажмите **↻** — столбец **Stock** у купленного товара уменьшился (остаток реально зарезервирован).

### Кейс 2. Компенсация через брокер (возврат остатка)

1. Нажмите кнопку **«demo: payment fail»** — она сама проставит `customer=fail`, добавит товар и запустит покупку.
2. Ожидаемый результат: красное сообщение **«❌ payment failed, compensated»** (HTTP 402, под ним причина `card declined (mock: customer=fail)`) и трасса:
   - `3. PAYMENT failed: card declined ... -> publish order.cancelled (compensation)` 🔴
   - `4. COMPENSATION ok via broker: reservation ... cancelled, stock restored (stock.cancelled)` 🔴
3. В **Orders** — плашка **CANCELLED**. В **Catalog** нажмите **↻** — остаток товара **вернулся**: компенсация дошла до каталога через брокер.

### Кейс 3. Отказ резерва без компенсации

1. Нажмите **«demo: out-of-stock #17»** (товар 17 всегда с нулевым остатком).
2. Ожидаемый результат: **«❌ reserve failed»** (HTTP 409, под ним причина из каталога), в **Orders** плашка **FAILED**, в трассе только:
   - `1. ... (transport=broker: publish order.created)`
   - `2. RESERVE failed via broker -> abort: ...` 🔴
   Шагов 3–4 (платёж, компенсация) нет — и это правильно: отказался резерв, остаток не тронут.

### Как по трассе отличить брокер от fallback

- `transport=broker: publish ...`, `via broker`, `stock.reserved/confirmed/cancelled` — путь **через RabbitMQ**, всё корректно.
- `transport=http` и шаги без «via broker» — брокер не поднялся при старте сервисов, сага пошла по **HTTP-fallback**. Это не ошибка работы саги, но событийную проверку пройти не удалось: перезапустите сервисы, когда RabbitMQ доступен (`docker compose restart orders catalog`), и повторите Кейс 1.

### Кейс 4 (опционально). Смотрим сами сообщения в RabbitMQ

Пока идут заказы, откройте **http://localhost:15672** (guest/guest):

1. **Exchanges → `shop`** — тип `topic`, должны расти счётчики `Publish` / `Deliver`.
2. **Queues → `catalog.order-events` (binding `order.*`) и `orders.stock-events` (binding `stock.*`)** — вкладки **Overview** с графиками **Message rates**: видно, как события поступают и тут же потребляются (очереди должны оставаться пустыми или почти пустыми — потребители читают их с prefetch 10/20).

Именно эти четыре кейса вместе подтверждают, что брокер работает: сообщение ушло в exchange, дошло до очереди, потребитель обработал его, а ответное событие вернулось и корректно завершило (или скомпенсировало) сагу.

## Таблица API

| Gateway | Проксируется на |
|---------|-----------------|
| `GET /api/products` | `GET catalog/products` |
| `GET /api/products/{id}` | `GET catalog/products/{id}` |
| `GET /api/orders` | `GET orders/orders` |
| `POST /api/checkout` | `POST orders/orders/checkout` (сага поверх брокера) |
| `POST /api/orders` | `POST orders/orders` (устаревший) |
