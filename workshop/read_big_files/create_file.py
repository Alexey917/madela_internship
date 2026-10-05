from pathlib import Path

path = Path('madela_internship/workshop/read_big_files')

with open(path / 'big_file.txt', 'w', encoding='utf-8') as f:
    for i in range(1_000_000):
        f.write(f'Строка номер {i}: тестовые данные для проверки генератора\n')