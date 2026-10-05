import logging, sys, signal, time
from functools import wraps


sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8') 

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)7s - %(message)s',
)

class MyTimeoutError(TimeoutError):
    pass


def throw_exception(sig, frm):
    raise MyTimeoutError('Функция превысила время допустимого выполнения!')

def function_stop_expired(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            signal.signal(signal.SIGALRM, throw_exception)
            signal.alarm(5)
            logging.info('Таймер запущен')
            res = func(*args, **kwargs)
            logging.info('Функция %s завершилась вовремя', func.__name__)
            return res
        finally:
            signal.alarm(0)
            logging.info('Таймер остановлен')
    return wrapper

@function_stop_expired
def long_function(delay):
    time.sleep(delay)


# long_function(7)
long_function(2)