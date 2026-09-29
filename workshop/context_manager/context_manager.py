import time
import logging

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)7s - %(message)s',
)

class Timer:
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.elapsed = None
    

    def __enter__(self):
        self.start_time = time.perf_counter()
        logging.info('Timer "%s" started', self.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start_time
        if exc_type is None: 
            logging.info('Timer "%s" finished in %.6f s', self.name, self.elapsed)
        else:
            logging.warning('Timer "%s" failed after %.6f s: %s', self.name, self.elapsed, exc_type.__name__)

        return False


with Timer('quick op') as timer:
    time.sleep(0.05)

try:
    timer = Timer('failing op')
    with timer:
        time.sleep(0.02)
        raise ValueError("error")
except ValueError:
    print("ValueError went outside, but the timer didn't swallow him")