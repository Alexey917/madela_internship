- [x] 17: **Каркас + инфра**
  - [x] 17.1: Тоже что и в 10 пункте (Inventory)

- [x] 18: **модель + Alembic**
  - [x] 18.1: Тоже самое что и в пункте 2 Catalog
  - [x] 18.2: Т.к порты не через localhost, то миграцию нужно сделать иначе docker compose exec payment alembic revision --autogenerate -m "create payments table" - если порт у бд не через localhost. В докере будет, в папке не будет
  - [x] 18.3: Скопировать файл миграции из контейнера на хост(в папку): docker compose cp payment:/app/alembic/versions/6c68263af20f_create_payments_table.py ./alembic/versions/
  - [x] 18.4: docker compose exec payment alembic upgrade head создать миграцию

- [x] 19: **Mock-шлюз + tenacity**
  - [x] 19.1: Добавление зависимости: poetry add tenacity httpx

