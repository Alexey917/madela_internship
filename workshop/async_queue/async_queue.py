import asyncio, aiohttp, sys, logging

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8') 

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(module)s:%(lineno)d %(levelname)7s - %(message)s',
)

async def producer(queue, urls, session):
    for url in urls:
        async with session.get(url) as resp:
            data = await resp.json()
            await queue.put(data.get("name"))
            logging.info('%s добавлен в очередь', data.get("name"))
    await queue.put(None)
    await queue.put(None)
    logging.info('Больше нет пользователей')
    

async def first_consumer(queue, name):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            logging.info('Очередь пуста')
            break
        queue.task_done()
        logging.info('Обработан пользователь из %s: %s', name, item)


async def second_consumer(queue, name):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            logging.info('Очередь пуста')
            break
        queue.task_done()
        logging.info('Обработан пользователь из %s: %s', name, item)


async def main():
    async with aiohttp.ClientSession() as session:
        q = asyncio.Queue()
        urls = [f'https://jsonplaceholder.typicode.com/users/{i}' for i in range(1, 11)]
        task_producer = asyncio.create_task(producer(q, urls, session))
        consumer_task_1 = asyncio.create_task(first_consumer(q, "first_consumer"))
        consumer_task_2 = asyncio.create_task(second_consumer(q, "second_consumer"))

        await q.join()
        await task_producer
        await consumer_task_1
        await consumer_task_2


asyncio.run(main())