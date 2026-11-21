# SAGA (orchestration)

Order Service — оркестратор. Состояния:
`PENDING → RESERVED → PAID → COMPLETED`
либо
`FAILED → COMPENSATING → CANCELLED`.

## Happy path

```mermaid
sequenceDiagram
    autonumber
    participant C as Client (UI)
    participant O as Order
    participant RMQ as RabbitMQ
    participant I as Inventory
    participant P as Payment
    participant N as Notification

    C->>O: POST /orders (Idempotency-Key)
    O->>O: create order PENDING, save saga state
    O->>RMQ: inventory.reserve
    RMQ->>I: inventory.reserve
    I->>I: reserve stock
    I->>RMQ: inventory.reserved
    RMQ->>O: inventory.reserved
    O->>O: state = RESERVED
    O->>RMQ: payment.process
    RMQ->>P: payment.process
    P->>P: charge (mock gateway)
    P->>RMQ: payment.succeeded
    RMQ->>O: payment.succeeded
    O->>O: state = PAID → COMPLETED
    O->>RMQ: notification.send
    RMQ->>N: notification.send
    N->>N: send email (mock) + idempotency
```

## Compensation path

```mermaid
sequenceDiagram
    autonumber
    participant C as Client (UI)
    participant O as Order
    participant RMQ as RabbitMQ
    participant I as Inventory
    participant P as Payment
    participant N as Notification

    C->>O: POST /orders (Idempotency-Key)
    O->>O: create order PENDING
    O->>RMQ: inventory.reserve
    RMQ->>I: inventory.reserve
    I->>RMQ: inventory.reserved
    RMQ->>O: inventory.reserved
    O->>O: state = RESERVED
    O->>RMQ: payment.process
    RMQ->>P: payment.process
    P->>RMQ: payment.failed
    RMQ->>O: payment.failed
    O->>O: state = FAILED → COMPENSATING
    O->>RMQ: inventory.release
    RMQ->>I: inventory.release
    I->>I: release stock
    I->>RMQ: inventory.released
    RMQ->>O: inventory.released
    O->>O: state = CANCELLED
    O->>RMQ: notification.send
    RMQ->>N: notification.send
    N->>N: send failure email
```

## Идемпотентность
- Все мутирующие endpoints принимают `Idempotency-Key`.
- Ключи в Redis (TTL 24 ч) + запись в БД для аудита.
- Повторный запрос с тем же ключом → тот же результат, без повторного списания/резерва.

## Outbox
- Таблица `outbox` в order, inventory, payment.
- Фоновый воркер публикует события в RabbitMQ.
- Гарантия at-least-once; consumer'ы идемпотентны.

## Retry
- `tenacity`, экспоненциальная задержка 1→2→4→8 с, 3–5 попыток.
- Только идемпотентные операции (публикация, чтение, refund).

## DLQ
- Очереди `*.dlq` для сообщений, не обработанных после N попыток.