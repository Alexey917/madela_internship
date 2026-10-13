import aiohttp, asyncio, time, sys, logging

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8') 

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(module)s:%(lineno)d %(levelname)7s - %(message)s',
)

sem = asyncio.Semaphore(5)
# sem = asyncio.Semaphore(3)
# sem = asyncio.Semaphore(1)

async def scraper(url, session):
    result = {}
    async with sem:
        async with session.get(url) as resp:
          data = await resp.json()
          result["url"] = str(resp.url)
          result["status"] = resp.status
          result["username"] = data.get("username")
          logging.info('%s', result)
          return result


async def main():
  async with aiohttp.ClientSession() as session:
      start = time.perf_counter()
      urls = [f'https://jsonplaceholder.typicode.com/users/{i}' for i in range(1, 11)]
      result = await asyncio.gather(*[scraper(url, session) for url in urls])
      elapsed = time.perf_counter() - start

      logging.info('Время выполнения: %.6fs, длина: %s', elapsed, len(result))

  
asyncio.run(main())





