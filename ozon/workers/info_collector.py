import pandas as pd

from config import MAIN_DIR, REMOTE_PATH
from ozon.ozon_config import LOCAL_RETURNS_PATH, LOCAL_ORDERS_PATH, YANDEX_DISC_RETURNS_FILE_NAME, YANDEX_DISC_ORDERS_FILE_NAME
from ozon.dto.info_dto import InfoDTO
from ozon.services.ozon_service import OzonService
from ozon.utils.date_helpers import get_month_ago_iso, get_last_sunday_end_iso, date_month_ago, end_of_last_week
from yandex_disk import download_file


class InfoCollector:
    def __init__(self):
        self.ozon_service = OzonService()

    def collect_info(self) -> InfoDTO:
        download_file(REMOTE_PATH + YANDEX_DISC_RETURNS_FILE_NAME, LOCAL_RETURNS_PATH)
        download_file(REMOTE_PATH + YANDEX_DISC_ORDERS_FILE_NAME, LOCAL_ORDERS_PATH)

        cards_info = self.ozon_service.get_cards_info()

        time_from = date_month_ago() # '2026-04-27T00:00:00+00:00'
        time_to = end_of_last_week() # '2026-05-03T23:59:59+00:00'

        returns = self.ozon_service.get_returns(time_from, time_to)
        all_returns = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_RETURNS_FILE_NAME}')

        # "time_from": date_month_ago(), # "2026-04-27T00:00:00Z"
        # "time_to": end_of_last_week() # "2026-05-03T23:59:59Z"

        processed_at_from = get_month_ago_iso() # "2026-04-27T00:00:00Z"
        processed_at_to = get_last_sunday_end_iso() # "2026-05-03T23:59:59Z"

        orders = self.ozon_service.get_orders(processed_at_from, processed_at_to)
        all_orders = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}')

        return InfoDTO(
            cards_info=cards_info,
            orders=orders,
            returns=returns,
            all_orders=all_orders,
            all_returns=all_returns,
        )