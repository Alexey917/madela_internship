import sys, time, logging

from functools import wraps
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8') 

path = Path('madela_internship/workshop/retry')

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)7s - %(message)s',
)

def retry(repeat, delay):
    if repeat < 1:
        raise ValueError('Количество попыток не может быть меньше 1!')
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            times = 1
            while times <= repeat:
                try:
                    logging.info('Функция %s выполняется', func.__name__)
                    res = func(*args, **kwargs)
                    logging.info('Функция %s выполнилась успешно!', func.__name__)
                    return res
                except Exception as e:
                    logging.warning('Ошибка %s в выполнении функции %s', e, func.__name__)
                    if times == repeat:
                        logging.warning('Попытки повторного вызова исчерпаны')
                        raise
                    times += 1
                    logging.info('Повторный вызов %s через %s', func.__name__, delay) 
                    time.sleep(delay)
        return wrapper
    return decorator


@retry(repeat=4, delay=5)
def some_func(file: str):
    full_path = path / file
    try:
        with open(full_path, encoding='utf-8') as f:
            data = f.readline()
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f'Файл не найден: {full_path}')


some_func('products.tx')
# some_func('products.txt')



