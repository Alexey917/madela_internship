## Inventory Service

- [x] 10: **каркас + инфра**
  - [x] 10.1: Тоже самое что и в пункте 1 Catalog
  - [x] 10.2: Тоже самое что и в пункте 7 Catalog

- [x] 11: **модель + Alembic + sed**
  - [x] 11.1: Тоже самое что и в пункте 2 Catalog
  - [x] 11.2: Создание seed.py в папке scripts
  - [x] 11.3: Добавление запуска seed в entrypoint.sh: python -m scripts.seed
  - [x] 11.4: Проверка бд: docker exec -it projects-inventory-postgres-1 psql -U inventory -d inventory_db \
  -c "SELECT product_id, available, reserved FROM stock ORDER BY product_id;"

- [x] 12: **repository**
  - [x] 12.1: Тоже самое что и в пункте 3 Catalog
  - [x] 12.2: Сброс данных после теста: docker exec -it projects-inventory-postgres-1 psql -U inventory -d inventory_db \
  -c "UPDATE stock SET available=3, reserved=0 WHERE product_id=9;"

