import pandas as pd

from config import MAIN_DIR, REMOTE_PATH
from wb.wb_config import YANDEX_DISC_SALES_FILE_NAME, YANDEX_DISC_ORDERS_FILE_NAME, LOCAL_SALES_PATH, LOCAL_ORDERS_PATH
from wb.dto.info_dto import InfoDTO

from wb.services.wb_service import WBService
from wb.utils.date_helpers import get_two_weeks_range
from yandex_disk import download_file


class InfoCollector:
    def __init__(self):
        self.wb = WBService()

    def collect_info(self) -> InfoDTO:
        # date_from, date_to = '2026-06-01','2026-06-07'
        date_from, date_to = get_two_weeks_range()
        orders = self.wb.get_orders(date_from=date_from, date_to=date_to)
        sales = self.wb.get_sales(date_from=date_from, date_to=date_to)

        return InfoDTO(
            orders=orders,
            sales=sales,
        )
