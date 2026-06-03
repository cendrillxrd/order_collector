import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DATA_LIST_NAME = 'Данные'
BASE_INFO_LIST_NAME = 'Сводная'
YANDEX_DISC_PIVOT_TABLE_FILE_NAME = '/Сводная по неделям.xlsx'
LOCAL_PIVOT_TABLE_PATH = f'.{YANDEX_DISC_PIVOT_TABLE_FILE_NAME}'

YANDEX_DISC_API_KEY = os.getenv('YANDEX_DISC_API_KEY')
REMOTE_PATH = '/Выгрузка из базы'

MAIN_DIR = f'{str(Path(__file__).parent)}'
