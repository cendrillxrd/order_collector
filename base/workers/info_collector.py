import pandas as pd

from base.dto.columns_main_dto import ColumnsBaseDTO
from base.config import YANDEX_DISC_BASE_FILE_NAME, LOCAL_PATH
from config import MAIN_DIR, REMOTE_PATH
from yandex_disk import download_file

class InfoCollector:
    def __init__(self):
        self.columns = ColumnsBaseDTO()
    def collect_info(self):
        download_file(REMOTE_PATH + YANDEX_DISC_BASE_FILE_NAME, LOCAL_PATH)
        df = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_BASE_FILE_NAME}')

        # Словарь с названиями сайтов и соответствующими фильтрами
        site_filters = {
            'Проект THE HILLS': 'Сайт THE HILLS',
            'Проект MARC CONY': 'Сайт MC',
            'Проект VAN MICH': 'Сайт VAN MICH',
            'МЁД': 'Сайт Мёд',
            'Приложение': 'Приложение',
            'Проект VipAvenue': 'VipAvenue'
        }

        # Создание словаря с DataFrames
        dataframes = {
            key: df[df[self.columns.canal] == filter_name].copy()
            for key, filter_name in site_filters.items()
        }

        return dataframes
