import pandas as pd

from config import MAIN_DIR, REMOTE_PATH
from ozon.config import LOCAL_RETURNS_PATH, LOCAL_ORDERS_PATH, YANDEX_DISC_RETURNS_FILE_NAME, YANDEX_DISC_ORDERS_FILE_NAME
from ozon.dto.info_dto import InfoDTO
from ozon.services.med import MEDService
from ozon.services.ozon_service import OzonService
from yandex_disk import download_file


class InfoCollector:
    def __init__(self):
        self.ozon_service = OzonService()
        self.med = MEDService()

    def collect_info(self) -> InfoDTO:
        download_file(REMOTE_PATH + YANDEX_DISC_RETURNS_FILE_NAME, LOCAL_RETURNS_PATH)
        download_file(REMOTE_PATH + YANDEX_DISC_ORDERS_FILE_NAME, LOCAL_ORDERS_PATH)

        cards_info = self.ozon_service.get_cards_info()
        returns = self.ozon_service.get_returns()
        all_returns = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_RETURNS_FILE_NAME}')
        orders = self.ozon_service.get_orders()
        all_orders = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}')

        return InfoDTO(
            cards_info=cards_info,
            orders=orders,
            returns=returns,
            all_orders=all_orders,
            all_returns=all_returns,
        )