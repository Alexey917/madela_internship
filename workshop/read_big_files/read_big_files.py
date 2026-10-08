import sys, logging
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8') 

path = Path('madela_internship/workshop/read_big_files')

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)7s - %(message)s',
)


def read_big_files(file_obj):
    for line in file_obj:
      yield line


with open(path / 'big_file.txt', encoding='utf-8') as f:
    logging.info('Файл открыт для чтения')
    generator = read_big_files(f)
    for i, line in enumerate(generator, start=1):
        logging.info('%s', line.rstrip('\n'))
        if i == 10:
            break
    logging.info('Файл закрыт')

          


