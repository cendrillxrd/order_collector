import pandas as pd

from config import MAIN_DIR, REMOTE_PATH
from wb.wb_config import YANDEX_DISC_SALES_FILE_NAME, YANDEX_DISC_ORDERS_FILE_NAME, LOCAL_SALES_PATH, LOCAL_ORDERS_PATH
from wb.dto.info_dto import InfoDTO
from wb.dto.orders_columns_dto import OrdersColumnsDTO
from wb.dto.sales_columns_dto import SalesColumnsDTO
from wb.services.redaction_service import RedactionService
from yandex_disk import download_file, upload_file


class InfoRedactor:
    def __init__(self):
        self.red = RedactionService()
        self.orders_columns = OrdersColumnsDTO()
        self.sales_columns = SalesColumnsDTO()

    def redact_info(self, info: InfoDTO, get_new_info: bool = False) -> pd.DataFrame:
        if get_new_info:
            sales_all_info = self.red.merge_sales(info.all_sales, info.sales)
            sales_all_info.to_excel(f'{MAIN_DIR}{YANDEX_DISC_SALES_FILE_NAME}', index=False)
            upload_file(f'{MAIN_DIR}{YANDEX_DISC_SALES_FILE_NAME}', REMOTE_PATH + YANDEX_DISC_SALES_FILE_NAME)

            orders_all_info = self.red.merge_orders(info.all_orders, info.orders)
            orders_all_info.to_excel(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}', index=False)
            upload_file(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}', REMOTE_PATH + YANDEX_DISC_ORDERS_FILE_NAME)

            sales_main_info = self.red.get_sales_main_info(sales_all_info)
            orders_main_info = self.red.get_orders_main_info(orders_all_info)

            agg_table = self.red.merge_main_info(orders_main_info, sales_main_info)
            return agg_table
        else:
            download_file(REMOTE_PATH + YANDEX_DISC_SALES_FILE_NAME, LOCAL_SALES_PATH)
            download_file(REMOTE_PATH + YANDEX_DISC_ORDERS_FILE_NAME, LOCAL_ORDERS_PATH)

            sales_all_info = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_SALES_FILE_NAME}')

            orders_all_info = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}')

            sales_main_info = self.red.get_sales_main_info(sales_all_info)
            orders_main_info = self.red.get_orders_main_info(orders_all_info)

            agg_table = self.red.merge_main_info(orders_main_info, sales_main_info)
            return agg_table