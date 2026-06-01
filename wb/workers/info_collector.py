import pandas as pd

from config import MAIN_DIR
from wb.config import BASE_ORDERS_FILE_NAME, BASE_SALES_FILE_NAME
from wb.dto.info_dto import InfoDTO

from wb.services.wb_service import WBService
from wb.utils.date_helpers import get_last_week_dates, get_two_weeks_range


class InfoCollector:
    def __init__(self):
        self.wb = WBService()

    def collect_info(self) -> InfoDTO:
        date_from, date_to = get_two_weeks_range()
        orders = self.wb.get_orders(date_from=date_from, date_to=date_to)
        all_orders = pd.read_excel(f'{MAIN_DIR}/{BASE_ORDERS_FILE_NAME}.xlsx')
        sales = self.wb.get_sales(date_from=date_from, date_to=date_to)
        all_sales = pd.read_excel(f'{MAIN_DIR}/{BASE_SALES_FILE_NAME}.xlsx') # укажи путь

        return InfoDTO(
            orders=orders,
            sales=sales,
            all_sales=all_sales,
            all_orders=all_orders
        )
