import pandas as pd

from base.config import BASE_FILE_NAME
from base.dto.columns_main_dto import ColumnsBaseDTO
from config import MAIN_DIR


class InfoCollector:
    def __init__(self):
        self.columns = ColumnsBaseDTO()
    def collect_info(self):
        df = pd.read_excel(f'{MAIN_DIR}/{BASE_FILE_NAME}.xlsx')

        # Словарь с названиями сайтов и соответствующими фильтрами
        site_filters = {
            'Проект THE HILLS': 'Сайт THE HILLS',
            'Проект MARC CONY': 'Сайт MC',
            'Проект VAN MICH': 'Сайт VAN MICH',
            'МЁД': 'Сайт Мёд',
            'Приложение': 'Приложение'
        }

        # Создание словаря с DataFrames
        dataframes = {
            key: df[df[self.columns.canal] == filter_name].copy()
            for key, filter_name in site_filters.items()
        }

        return dataframes
