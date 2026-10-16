import asyncio, aiohttp, sys, logging

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8') 

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(module)s:%(lineno)d %(levelname)7s - %(message)s',
)

async def request_url(url, session):
    async with session.get(url) as resp:
        try:
            resp.raise_for_status()
            res = await resp.json()
            if not res:
                logging.info('Данные отсутствуют')
                return
            logging.info('Запрос успешно выполнен. Результат: %s', res)
            return res
        except asyncio.CancelledError:
            logging.error('Запрос %s был отменен', url)
            raise

        
async def main():
    async with aiohttp.ClientSession() as session:
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(request_url('https://jsonplaceholder.typicode.com/posts/1', session))
                tg.create_task(request_url('https://jsonplaceholder.typicode.com/posts/999999', session))
                tg.create_task(request_url('https://nonexistent-domain-xyz.com/', session))
                tg.create_task(request_url('https://httpbin.org/status/500', session))
        except* aiohttp.ClientResponseError as eg:
            for exc in eg.exceptions:
              logging.error('Ошибка %s: %s (%s)', exc.status, exc.message, exc.request_info.url)
        except* aiohttp.ClientConnectorError as eg:
            for exc in eg.exceptions:
              logging.error('Не удалось подключиться к %s:%s — %s', exc.host, exc.port, exc.os_error)
        except* Exception as eg:
            logging.error('Ошибка выполнения запроса: %s', eg.exceptions)
        

asyncio.run(main())