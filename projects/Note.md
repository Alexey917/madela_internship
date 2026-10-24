## Inventory Service

- [x] 10: **каркас + инфра**
  - [x] 10.1: Создание базовых файлов: .gitignore, Notes.md, README.md
  - [x] 10.2: Папка для сервиса services/inventory
  - [x] 10.3: Poetry + зависимости
  - [x] 10.3: Создание переменных окружения
  - [x] 10.4: Настройка postgres и redis в docker-compose.yml
  - [x] 10.5: config.py для чтения значений из окружения и пустой __init__.py
  - [x] 10.6: Создание приложения в main.py, подключение метрик и эндпоинт для проверки работоспособности
  - [x] 10.7: Проверки:
    - [x] 10.7.1 docker compose up -d 
    - [x] 10.7.2 docker compose ps
    - [x] 10.7.3 docker compose logs inventory проверка логов
    - [x] 10.7.3 poetry run uvicorn app.main:app --reload --port 8002
    - [x] 10.7.4 curl http://localhost:8002/health
    - [x] 10.7.5 curl -s http://localhost:8002/metrics | head