import time, logging, sys
from functools import wraps

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8') 

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)7s - %(message)s',
)

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            start_time = time.perf_counter()
            res = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            return res
        finally:
            logging.info('Функция выполнилась за %.6fs', elapsed)
    return wrapper


@timeit
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target: 
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return None
    
    
print('Индекс: ', binary_search(list(range(1, 5000, 2)), 39))
print('Индекс: ', binary_search(list(range(1, 100000, 2)), 103))
print('Индекс: ', binary_search(list(range(1, 1000000, 2)), 5))
print('Индекс: ', binary_search(list(range(1, 100000000, 2)), 4))