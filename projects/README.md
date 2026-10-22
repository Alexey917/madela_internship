# 🎲 Board Games Shop

Демонстрационный интернет-магазин настольных игр с микросервисной архитектурой, SAGA-оркестрацией и платёжным шлюзом.

## Статус

| Сервис | Статус |
|---|---|
| **Catalog** | ✅ Готов |
| Inventory | 🚧 В работе |
| Orders | ⏳ Ожидает |
| Payments | ⏳ Ожидает |
| Notifications | ⏳ Ожидает |
| API Gateway | ⏳ Ожидает |
| UI | ⏳ Ожидает |

## Стек

- **Python 3.12** + **FastAPI**
- **PostgreSQL 16** + **SQLAlchemy 2.0 (async)** + **Alembic**
- **Redis 7** — кеш каталога (TTL 60s), идемпотентность (позже)
- **RabbitMQ** — асинхронный обмен событиями (следующий этап)
- **Docker** + **docker-compose** — весь стек одной командой
- **Prometheus** — метрики

## Архитектура

Смотри [`docs/architecture.md`](docs/architecture.md) — C4 Context + Container.

## Быстрый старт

```bash
git clone <repo-url>
cd madela_internship/projects
docker compose up -d
