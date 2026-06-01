import logging
import sys
from pathlib import Path


def setup_logger(name="my_app"):
    logger = logging.getLogger(name)  # Используем фиксированное имя!

    # Если логгер уже настроен (уже есть обработчики), возвращаем его
    if logger.handlers:
        return logger

    # Уровень логирования
    logger.setLevel(logging.DEBUG)

    # Формат сообщений
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Путь к директории, где находится текущий скрипт
    current_dir = Path(__file__).resolve().parent

    # Запись в файл
    file_handler = logging.FileHandler(f'{current_dir}/app.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False

    return logger