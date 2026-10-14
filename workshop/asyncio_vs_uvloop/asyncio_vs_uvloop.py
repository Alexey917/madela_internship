import aiohttp, asyncio, time, sys, logging, uvloop

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8') 

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(module)s:%(lineno)d %(levelname)7s - %(message)s',
)


# sem = asyncio.Semaphore(3)
# sem = asyncio.Semaphore(1)

async def scraper(url, session, sem):
    result = {}
    async with sem:
        async with session.get(url) as resp:
          data = await resp.json()
          result["url"] = str(resp.url)
          result["status"] = resp.status
          result["title"] = data.get("title")
          return result


async def main():
  sem = asyncio.Semaphore(5)
  async with aiohttp.ClientSession() as session:
      urls = [f'https://jsonplaceholder.typicode.com/posts/{i}' for i in range(1, 101)]
      results = await asyncio.gather(*[scraper(url, session, sem) for url in urls])
      return len(results)


start = time.perf_counter()
with asyncio.Runner() as runner:
    count = runner.run(main())
elapsed = time.perf_counter() - start
logging.info('asyncio: %.6fs, обработано: %d', elapsed, count)


start = time.perf_counter()
with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
    count = runner.run(main())
elapsed = time.perf_counter() - start
logging.info('uvloop: %.6fs, обработано: %d', elapsed, count)