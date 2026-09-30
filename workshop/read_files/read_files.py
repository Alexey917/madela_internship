import json, csv, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8') 

path = Path('madela_internship/workshop/read_files')

def read_files(file: str):
    full_path = path / file
    file_format = file.rsplit('.', 1)[-1].lower()
    print(file_format)

    if file_format not in ('json', 'csv'):
        raise ValueError(f"Неподдерживаемый формат: {file_format}")

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            if file_format == 'json':
                data = json.load(f)
    
            if file_format == 'csv':
                data = list(csv.DictReader(f))
    except FileNotFoundError:
        raise FileNotFoundError(f'Файл не найден: {full_path}')
    except json.JSONDecodeError as e:
        raise ValueError(f'Некорректный json в {full_path}: {e}')
    except UnicodeDecodeError as e:
        raise ValueError(f'Ошибка кодировки в {full_path}: {e}')
    except csv.Error as e:
      raise ValueError(f'Ошибка CSV в {full_path}: {e}')

    return data

print(read_files('products.csv'))
print(read_files('products.json'))
print(read_files('products.txt'))

