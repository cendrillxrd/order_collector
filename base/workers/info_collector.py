import pandas as pd

from base.config import YANDEX_DISC_BASE_FILE_NAME, LOCAL_PATH
from base.dto.columns_main_dto import ColumnsBaseDTO
from base.repositories.db_repository import upsert_base_orders
from config import MAIN_DIR, REMOTE_PATH
from yandex_disk import download_file


class InfoCollector:
    def __init__(self):
        self.columns = ColumnsBaseDTO()

    @staticmethod
    def collect_info():
        download_file(REMOTE_PATH + YANDEX_DISC_BASE_FILE_NAME, LOCAL_PATH)
        df = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_BASE_FILE_NAME}')
        upsert_base_orders(df)