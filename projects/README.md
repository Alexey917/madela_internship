# 🎲 Board Games Shop

![Python](https://shields.io)
![FastAPI](https://shields.io)
![React](https://shields.io)
![PostgreSQL](https://shields.io)
![RabbitMQ](https://shields.io)
![Redis](https://shields.io)
![Nginx](https://shields.io)

> Микросервисный демонстрационный интернет-магазин настольных игр с реализацией распределённых транзакций по паттерну **SAGA (Orchestration)**, асинхронным обменом через **RabbitMQ** и эмуляцией платёжного шлюза.

---

##📑 Содержание
- [Технологический стек](#-технологический-стек)
- [Архитектура](#-архитектура)
- [Быстрый старт](#-быстрый-старт)
- [Сервисы и порты](#-сервисы-и-порты)
- [Демо-сценарии](#-демо-сценарии)
- [Примеры API-запросов (cURL)](#-примеры-api-запросов-curl)
- [Тестирование](#-тестирование)
- [Процесс разработки (GitFlow)](#-процесс-разработки-gitflow)
- [Лицензия](#-лицензия)

---

## 🛠 Технологический стек

| Категория | Технологии |
| :--- | :--- |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2 |
| **Базы данных** | PostgreSQL 16 *(Database-per-Service)* |
| **Кэш и идемпотентность** | Redis 7 |
| **Брокер сообщений** | RabbitMQ 3.13 *(с Management UI)* |
| **Frontend** | React, TypeScript, Ant Design |
| **API Gateway** | Nginx *(reverse proxy, JWT `auth_request`, CORS)* |
| **Мониторинг и логи** | Prometheus, Grafana, `structlog` (JSON) + Correlation ID |

---

## 🏗 Архитектура

Подробные схемы взаимодействия сервисов и описание шагов оркестрации:
- 📐 **[C4 Context + Container](docs/architecture.md)** — обзор компонентов системы и потоков данных.
- 🔄 **[SAGA-сценарии (Happy + Compensation)](docs/saga.md)** — диаграммы последовательности успешного заказа и компенсации.

---

## 🚀 Быстрый старт

### 1. Клонирование и запуск контейнеров
```bash
git clone https://github.com/Alexey917/madela_internship.git
cd madela_internship/projects
docker compose up -d --build
```

### 2. Проверка статуса сервисов
Дождитесь, пока все контейнеры перейдут в состояние `healthy`:
```bash
docker compose ps
```

### 3. Доступ к интерфейсам
- 🌐 **Веб-интерфейс (UI):** http://localhost:8080
- 🐇 **RabbitMQ Management UI:** http://localhost:15673 *(логин/пароль: `catalog` / `catalog`)*
- 📖 **Swagger API документация:** доступна по индивидуальным портам сервисов (см. таблицу ниже).

---

## 🔌 Сервисы и порты

| Сервис | URL | Описание |
| :--- | :--- | :--- |
| **Gateway (UI + API)** | http://localhost:8080 | Единая точка входа (Nginx) |
| **UI (напрямую)** | http://localhost:3000 | Режим отладки фронтенда |
| **Catalog** | http://localhost:8001/docs | Управление каталогом товаров (Swagger) |
| **Inventory** | http://localhost:8002/docs | Учёт остатков и резервирование (Swagger) |
| **Payment** | http://localhost:8003/docs | Эмуляция платёжного шлюза (Swagger) |
| **Order** | http://localhost:8004/docs | Оркестратор заказов и SAGA (Swagger) |
| **Notification** | http://localhost:8005/docs | Отправка уведомлений пользователям (Swagger) |
| **Auth** | http://localhost:8006/docs | Аутентификация и проверка JWT (Swagger) |
| **RabbitMQ UI** | http://localhost:15673 | Панель управления очередями (`catalog` / `catalog`) |

---

## 🎬 Демо-сценарии

### ✅ Happy Path (успешное оформление)
1. Откройте каталог товаров: http://localhost:8080.
2. Добавьте интересующую игру в корзину и нажмите **«Оформить заказ»**.
3. В модальном окне отслеживайте изменение статусов SAGA в реальном времени:
   ```text
   Ожидание ──▶ Зарезервировано ──▶ Оплачено ──▶ Завершено
   ```
4. Убедитесь, что пришло уведомление в сервис **Notification**, а заказ зафиксирован в БД со статусом `COMPLETED`.

### ⚠️ Compensation Path (откат при нехватке товара)
1. Попробуйте оформить заказ с количеством товара, превышающим доступный остаток на складе.
2. Сервис **Inventory** отклоняет резервирование и публикует событие `inventory.failed`.
3. Оркестратор **Order** запускает компенсирующую транзакцию и переводит заказ в статус `CANCELLED`.
4. В модальном окне таймлайн наглядно отобразит откат операции.

### ⚠️ Compensation Path (откат при неудачном платеже)
1. Добавьте интересующую игру в корзину и нажмите **«Оформить заказ»**.
2. В модальном окне отслеживайте изменение статусов SAGA в реальном времени:
3. Сервис **Payment** отклоняет платеж в 40% (Эмуляция платежного шлюза) и публикует событие `payment.failed`.
4. В модальном окне таймлайн наглядно отобразит откат операции.

---

## 💻 Примеры API-запросов (cURL)

<details>
<summary><b>Нажмите, чтобы развернуть примеры запросов</b></summary>

#### 1. Авторизация и получение токена
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"pvpuvk@yandex.ru","password":"user123"}'
```

#### 2. Получение списка товаров
```bash
curl http://localhost:8080/api/products
```

#### 3. Создание заказа (с ключом идемпотентности)
```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Authorization: Bearer <token>" \
  -H "Idempotency-Key: \$(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{"items":[{"product_id":1,"quantity":1}]}'
```

#### 4. Проверка статуса заказа
```bash
curl http://localhost:8080/api/orders/<order_id> \
  -H "Authorization: Bearer <token>"
```

</details>

---

## 🧪 Тестирование

Запуск unit- и интеграционных тестов с проверкой покрытия кода (минимум 70%) выполняется внутри директории нужного сервиса:

```bash
cd services/<service_name>
poetry run pytest --cov=app --cov-fail-under=70
```

---

## 🌿 Процесс разработки (GitFlow)

В репозитории используется модель ветвления **GitFlow** и спецификация **Conventional Commits**:
- `main` — стабильная продакшн-ветка.
- `develop` — основная ветка интеграции новых фич.
- `feature/*` — разработка новой функциональности.
- `release/*` — подготовка релизов.
- `hotfix/*` — срочные исправления.

---

## 📄 Лицензия

Учебный проект, разработанный в рамках стажировки.