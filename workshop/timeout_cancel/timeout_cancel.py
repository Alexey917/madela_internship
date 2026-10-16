import asyncio, sys, logging, time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8') 

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(module)s:%(lineno)d %(levelname)7s - %(message)s',
)

async def long_task(delay):
    elapsed = 0
    logging.info('Ожидаемое время выполнения функции %ss', delay)
    start = time.perf_counter()
    try:
        await asyncio.sleep(delay)
    except asyncio.CancelledError:
        logging.warning('Функция завершилась из-за отмены')
        raise
    finally:
        elapsed = time.perf_counter() - start
        logging.info('Функция выполнилась за (%.6fs)', elapsed)
    


async def main():
    delay = 7
    # delay = 10
    # delay = 15
    try:
        async with asyncio.timeout(10):
            await long_task(delay)
            logging.info('Штатное завершение функции')       
    except TimeoutError:
        logging.warning('Функция выполнялась слишком долго')
        

asyncio.run(main())
