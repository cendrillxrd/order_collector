import pandas as pd

from config import MAIN_DIR, REMOTE_PATH
from logger import setup_logger
from yandex.yandex_config import LOCAL_RETURNS_PATH, LOCAL_ORDERS_PATH
from yandex.yandex_config import YANDEX_DISC_RETURNS_FILE_NAME, YANDEX_DISC_ORDERS_FILE_NAME
from yandex.dto.info_yandex_dto import InfoYandexDTO
from yandex.services.med_service import MedService
# from dto.main_columns_dto import YandexColumnsDTO
# from dto.update_info_yandex_dto import InfoUpdateDTO
from yandex.services.yandex_service import YandexService
from yandex.utils.date_helper import get_date_30_days_before_last_week_end, get_current_week_monday, get_last_week_sunday
from yandex_disk import download_file

logger = setup_logger("my_app")


class InfoCollector:
    def __init__(self):
        self.yandex = YandexService()
        self.med = MedService()

    def collect_info(self) -> InfoYandexDTO:
        download_file(REMOTE_PATH + YANDEX_DISC_RETURNS_FILE_NAME, LOCAL_RETURNS_PATH)
        download_file(REMOTE_PATH + YANDEX_DISC_ORDERS_FILE_NAME, LOCAL_ORDERS_PATH)

        date_from = get_date_30_days_before_last_week_end()
        date_to = get_last_week_sunday()
        returns = self.yandex.get_returns(date_from=date_from, date_to=date_to)
        all_returns = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_RETURNS_FILE_NAME}')
        orders = self.yandex.get_orders()
        all_orders = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}')
        med_collections = self.med.get_med_collections()

        return InfoYandexDTO(
            orders=orders,
            returns=returns,
            all_orders=all_orders,
            all_returns=all_returns,
            med_collections=med_collections
        )