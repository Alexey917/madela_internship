# Development Notes

## Catalog Service

- [ ] 1: **каркас + инфра**
  - [ ] 1.1: Создание базовых файлов: .gitignore, Notes.md, README.md
  - [ ] 1.2: Папка для сервиса services/catalog
  - [ ] 1.3: Poetry + зависимости
  - [ ] 1.3: Создание переменных окружения
  - [ ] 1.4: Настройка postgres и redis в docker-compose.yml
  - [ ] 1.5: config.py для чтения значений из окружения и пустой __init__.py
  - [ ] 1.6: Создание приложения в main.py, подключение метрик и эндпоинт для проверки работоспособности
  - [ ] 1.7: Проверки:
    - [ ] 1.7.1 docker compose up -d 
    - [ ] 1.7.2 docker compose ps
    - [ ] 1.7.3 poetry run uvicorn app.main:app --reload --port 8001
    - [ ] 1.7.4 curl http://localhost:8001/health
    - [ ] 1.7.5 curl -s http://localhost:8001/metrics | head


- [ ] 2: модель + Alembic
- [ ] 3: repository
- [ ] 4: схемы + роутеры
- [ ] 5: кеш
- [ ] 6: seed
- [ ] 7: Dockerfile
- [ ] 8: README + проверка