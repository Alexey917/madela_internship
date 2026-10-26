# Архитектура

## C4 Level 1: System Context

```mermaid
C4Context
    title System Context — Board Games Shop

    Person(customer, "Покупатель", "Смотрит каталог, оформляет заказ")
    Person(admin, "Администратор", "Управляет товарами")

    System(shop, "Board Games Shop", "Интернет-магазин настольных игр с SAGA")

    System_Ext(payment, "Платёжный шлюз", "Stripe / ЮKassa (sandbox)")
    System_Ext(notify, "Email/SMS шлюз", "Эмуляция уведомлений")

    Rel(customer, shop, "Просматривает, покупает", "HTTPS")
    Rel(admin, shop, "Управляет каталогом", "HTTPS")
    Rel(shop, payment, "Списывает / возвращает", "HTTPS")
    Rel(shop, notify, "Отправляет уведомления", "SMTP / API")