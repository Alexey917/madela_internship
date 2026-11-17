import asyncio

from decimal import Decimal
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Product

SEED_PRODUCTS = [
  {
    "name": "Каркассон",
    "publisher": "Hobby World",
    "min_players": 2,
    "max_players": 5,
    "play_time_minutes": 45,
    "min_age": 8,
    "price": Decimal("2990.00"),
    "stock": 15,
    "description": "Классическая игра о строительстве средневековых городов и дорог.",
  },
  {
    "name": "Catan",
    "publisher": "Hobby World",
    "min_players": 3,
    "max_players": 4,
    "play_time_minutes": 90,
    "min_age": 10,
    "price": Decimal("3490.00"),
    "stock": 20,
    "description": "Колонизация острова Катан: ресурсы, торговля, строительство.",
  },
  {
    "name": "Манчкин",
    "publisher": "Hobby World",
    "min_players": 3,
    "max_players": 6,
    "play_time_minutes": 60,
    "min_age": 12,
    "price": Decimal("1490.00"),
    "stock": 50,
    "description": "Пародийная карточная игра про подземелья и монстров.",
  },
  {
    "name": "Codenames",
    "publisher": "Стиль Жизни",
    "min_players": 2,
    "max_players": 8,
    "play_time_minutes": 15,
    "min_age": 14,
    "price": Decimal("1990.00"),
    "stock": 30,
    "description": "Командная игра на ассоциации и угадывание слов.",
  },
  {
    "name": "Билет на поезд",
    "publisher": "Hobby World",
    "min_players": 2,
    "max_players": 5,
    "play_time_minutes": 60,
    "min_age": 8,
    "price": Decimal("3990.00"),
    "stock": 10,
    "description": "Строительство железных дорог и выполнение маршрутов.",
  },
  {
    "name": "Диксит",
    "publisher": "Стиль Жизни",
    "min_players": 3,
    "max_players": 6,
    "play_time_minutes": 30,
    "min_age": 8,
    "price": Decimal("2490.00"),
    "stock": 25,
    "description": "Игра на воображение с ассоциативными картами.",
  },
  {
    "name": "7 Wonders",
    "publisher": "Стиль Жизни",
    "min_players": 3,
    "max_players": 7,
    "play_time_minutes": 30,
    "min_age": 10,
    "price": Decimal("4490.00"),
    "stock": 12,
    "description": "Развитие цивилизаций и строительство чудес света.",
  },
  {
    "name": "Splendor",
    "publisher": "Hobby World",
    "min_players": 2,
    "max_players": 4,
    "play_time_minutes": 30,
    "min_age": 10,
    "price": Decimal("3490.00"),
    "stock": 18,
    "description": "Торговля драгоценными камнями и развитие бизнеса.",
  },
  {
    "name": "Gloomhaven",
    "publisher": "Hobby World",
    "min_players": 1,
    "max_players": 4,
    "play_time_minutes": 120,
    "min_age": 14,
    "price": Decimal("12990.00"),
    "stock": 3,
    "description": "Кампанейская игра в жанре тактической RPG.",
  },
  {
    "name": "Azul",
    "publisher": "Стиль Жизни",
    "min_players": 2,
    "max_players": 4,
    "play_time_minutes": 45,
    "min_age": 8,
    "price": Decimal("3290.00"),
    "stock": 8,
    "description": "Абстрактная игра о выкладывании плиток.",
  },
  {
    "name": "Смертельные материалы",
    "description": "Помогите незнакомцам пройти ряд комнат с опасными испытаниями, избежать гибели и вспомнить, как все они между собой связаны. Это карточный квест-детектив с логическими и дедуктивными загадками, атмосферой хоррора и необычной механикой.",
    "publisher": "HOBBY WORLD",
    "min_players": 1,
    "max_players": 6,
    "play_time_minutes": 30,
    "min_age": 18,
    "stock": 14,
    "price": Decimal("500.00")
  },
  {
    "name": "Морской бой",
    "description": "Перед Вами увлекательная настольная игра – «Морской бой». В нее можно играть снова и снова! Ведь в наборе есть все необходимое для победы над соперником. Играйте дома и в дороге, ведь магнитные фишки крепко держатся на металлическом поле. А еще их так удобно хранить в жестяной коробочке!",
    "publisher": "Десятое королевство",
    "min_players": 2,
    "max_players": 15,
    "play_time_minutes": 15,
    "min_age": 5,
    "stock": 7,
    "price": Decimal("500.00")
  },
  {
    "name": "Замки и зайчики",
    "publisher": "HOBBY WORLD",
    "min_players": 3,
    "max_players": 5,
    "play_time_minutes": 30,
    "min_age": 8,
    "price": Decimal("999.00"),
    "stock": 12,
    "description": "Тень пала на Заячье королевство! Таинственные чужеземцы свергли короля и посадили на трон самозванца-кролика. Но наследники не собираются мириться с захватом замка. Соберите отряды зайчиков и хитростью проложите себе путь к морковному трону!",
  },
  {
    "name": "Игра престолов",
    "publisher": "HOBBY WORLD",
    "min_players": 3,
    "max_players": 6,
    "play_time_minutes": 180,
    "min_age": 13,
    "price": Decimal("5243.00"),
    "stock": 10,
    "description": "Король Роберт Баратеон мертв, а земли Вестероса готовятся к сражениям…",
  },
  {
    "name": "Обитель тьмы",
    "publisher": "Magellan",
    "min_players": 3,
    "max_players": 5,
    "play_time_minutes": 50,
    "min_age": 13,
    "price": Decimal("3990.00"),
    "stock": 7,
    "description": "Вокруг тьма. Между небрежно вытесанных стен едва хватает места, чтобы протиснуться. Холодный камень царапает кожу. Где вы? Как вы оказались здесь? Понять это не представляется возможным – равно как и осмотреться. Единственный источник освещения – тусклая свеча в ваших руках.",
  },
  {
    "name": "Войны Чёрной Розы",
    "publisher": "HOBBY WORLD",
    "min_players": 2,
    "max_players": 2,
    "play_time_minutes": 45,
    "min_age": 13,
    "price": Decimal("4990.00"),
    "stock": 6,
    "description": "Германия, сельская местность, болота. Там, вдали от любопытных людских взглядов, стоит древняя тамплиерская крепость, таящая в себе секретов во сто крат больше, чем может представить себе человек.",
  },
  {
    "name": "Взрывные котята",
    "publisher": "HOBBY WORLD",
    "min_players": 2,
    "max_players": 5,
    "play_time_minutes": 15,
    "min_age": 10,
    "price": Decimal("750.00"),
    "stock": 11,
    "description": "Вот вам загадка – вместе с нами на Земле проживает более пятисот миллионов этих милейших созданий, фото и видео с их участием набирают невероятную популярность в интернете, мы очень любим их гладить, чесать им пузико и щекотать подушечки ног… Речь, конечно же, про любимых котеек!",
  },
  {
    "name": "Смешанный лес",
    "publisher": "Стиль Жизни",
    "min_players": 2,
    "max_players": 5,
    "play_time_minutes": 60,
    "min_age": 10,
    "price": Decimal("2490.00"),
    "stock": 4,
    "description": "Холмы Дартмура скрывают целый отдельный мир: у журчащих ручьёв порхают бабочки, а среди вереска бродят пони и овцы. Здесь каждый уголок наполнен жизнью, и вам предстоит собрать собственную маленькую экосистему, где растения и животные будут дополнять друг друга!",
  },
  {
    "name": "Root",
    "publisher": "Crown Games",
    "min_players": 2,
    "max_players": 4,
    "play_time_minutes": 90,
    "min_age": 10,
    "price": Decimal("4990.00"),
    "stock": 2,
    "description": "Root – это настольная игра о приключениях и войне, в которой от двух до четырёх игроков сражаются за контроль над обширным лесом.",
  },
  {
    "name": "Ярость Дракулы",
    "publisher": "HOBBY WORLD",
    "min_players": 2,
    "max_players": 5,
    "play_time_minutes": 180,
    "min_age": 13,
    "price": Decimal("3990.00"),
    "stock": 15,
    "description": "Избавьте Европу от влияния графа",
  },
  {
    "name": "Остров духов",
    "publisher": "HOBBY WORLD",
    "min_players": 1,
    "max_players": 4,
    "play_time_minutes": 120,
    "min_age": 13,
    "price": Decimal("7990.00"),
    "stock": 20,
    "description": "Давайте перенесёмся в дальние края далёкого мира, где ещё существует множество неизведанных земель и есть силы, неподвластные человеку. Представьте, что мы летим над бескрайним океаном и спускаемся ниже лишь тогда, когда натыкаемся на остров, где люди ещё живут в полной гармонии с природой. Вы – дух природы, который этому способствует и охраняет этот нетронутый рай.",
  },
  {
    "name": "Цитадели Классика",
    "publisher": "HOBBY WORLD",
    "min_players": 2,
    "max_players": 7,
    "play_time_minutes": 60,
    "min_age": 10,
    "price": Decimal("1490.00"),
    "stock": 9,
    "description": "Звание главного строителя королевства – это не только высочайшая честь для тех, кто посвятил свою жизнь возведению зданий, но и немалое количество преференций от монарха. Но чтобы его получить, недостаточно просто строить, возводить прекраснейшие достопримечательности и определять на века внешний вид города.",
  },
  {
    "name": "Битва за Рокуган",
    "publisher": "HOBBY WORLD",
    "min_players": 2,
    "max_players": 5,
    "play_time_minutes": 90,
    "min_age": 13,
    "price": Decimal("3990.00"),
    "stock": 8,
    "description": "Будьте мудрым даймё!",
  },
  {
    "name": "Монополия",
    "publisher": "Hasbro",
    "min_players": 2,
    "max_players": 6,
    "play_time_minutes": 120,
    "min_age": 8,
    "price": Decimal("4999.00"),
    "stock": 30,
    "description": "Приготовьтесь построить собственную финансовую империю вместе с легендарной 'Монополией'! Всё начинается с нескольких купюр и первого броска кубиков, а закончиться может огромным состоянием... или полным банкротством.",
  }
]


async def seed() -> None:
    async with SessionLocal() as session:
        created = 0
        skipped = 0

        for product in SEED_PRODUCTS:
            existing = await session.execute(select(Product.id).where(Product.name == product["name"]).limit(1))

            if existing.scalar_one_or_none() is not None:
                skipped += 1
                continue

            session.add(Product(**product))
            created += 1

        await session.commit()

    print(f"✅ Seed done: created={created}, skipped={skipped}")


if __name__ == "__main__":
    asyncio.run(seed())

            