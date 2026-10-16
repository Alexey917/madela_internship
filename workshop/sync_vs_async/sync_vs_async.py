import aiohttp, requests, sys, logging, time, asyncio

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8') 

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(module)s:%(lineno)d %(levelname)7s - %(message)s',
)

urls = [f'https://jsonplaceholder.typicode.com/posts/{i}' for i in range(1, 101)]

def sync_func(urls, session): 
    results = []
    
    for url in urls:
        with session.get(url) as resp:
            result = {}
            result["url"] = str(resp.url)
            result["status"] = resp.status_code
            result["title_len"] = len(resp.json().get("title"))
            results.append(result)
    return results


async def async_func(url, session):
    async with session.get(url) as resp:
        result = {}
        data = await resp.json()
        result["url"] = str(resp.url)
        result["status"] = resp.status
        result["title_len"] = len(data.get("title"))
        return result
    

async def main():
    async with aiohttp.ClientSession() as session:
        start = time.perf_counter()
        results = await asyncio.gather(*[async_func(url, session) for url in urls])
        elapsed = time.perf_counter() - start
        logging.info('%s', results)
        logging.info('Время выполнение асинхронной операции:  %.6fs', elapsed)
    start = time.perf_counter()
    with requests.Session() as session:
        results = sync_func(urls, session)
    elapsed = time.perf_counter() - start   
    logging.info('Время выполнение синхронной операции:  %.6fs', elapsed)
    logging.info('%s', results)


asyncio.run(main())