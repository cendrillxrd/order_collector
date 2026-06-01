import pandas as pd

from config import MAIN_DIR
from logger import setup_logger
from yandex.config import BASE_ORDERS_FILE_NAME, BASE_RETURNS_FILE_NAME
from yandex.dto.info_yandex_dto import InfoYandexDTO
from yandex.services.med import MedService
# from dto.main_columns_dto import YandexColumnsDTO
# from dto.update_info_yandex_dto import InfoUpdateDTO
from yandex.services.yandex_service import YandexService
from yandex.utils.date_helper import get_date_30_days_after_last_week_end, get_current_week_monday, get_last_week_sunday

logger = setup_logger("my_app")


class InfoCollector:
    def __init__(self):
        self.yandex = YandexService()
        self.med = MedService()

    def collect_info(self) -> InfoYandexDTO:
        date_from = get_date_30_days_after_last_week_end()
        date_to = get_last_week_sunday()
        returns = self.yandex.get_returns(date_from=date_from, date_to=date_to)
        all_returns = pd.read_excel(f'{MAIN_DIR}/{BASE_RETURNS_FILE_NAME}.xlsx')
        orders = self.yandex.get_orders()
        all_orders = pd.read_excel(f'{MAIN_DIR}/{BASE_ORDERS_FILE_NAME}.xlsx')
        med_collections_1 = self.med.get_med_collections_first()
        med_collections_2 = self.med.get_med_collections_second()
        med_collections_3 = self.med.get_med_collections_third()
        med_collections_4 = self.med.get_med_collections_fourth()

        return InfoYandexDTO(
            orders=orders,
            returns=returns,
            all_orders=all_orders,
            all_returns=all_returns,
            med_collection_1=med_collections_1,
            med_collection_2=med_collections_2,
            med_collection_3=med_collections_3,
            med_collection_4=med_collections_4,
        )