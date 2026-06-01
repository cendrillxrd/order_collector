import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DATA_LIST_NAME = 'Данные'
BASE_INFO_LIST_NAME = 'Сводная'
EXCEL_FILE_NAME = 'Сводная по неделям'

YANDEX_DISC_API_KEY = os.getenv('YANDEX_DISC_API_KEY')
REMOTE_PATH = '/Выгрузка из базы/База.xlsx'
LOCAL_PATH = './База.xlsx'

MAIN_DIR = f'{str(Path(__file__).parent)}'
