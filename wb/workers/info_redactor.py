import pandas as pd

from config import MAIN_DIR, REMOTE_PATH
from wb.repositories.db_repository import upsert_orders, upsert_sales, read_orders, read_sales
from wb.wb_config import YANDEX_DISC_SALES_FILE_NAME, YANDEX_DISC_ORDERS_FILE_NAME
from wb.dto.info_dto import InfoDTO
from wb.services.redaction_service import RedactionService
from yandex_disk import upload_file


class InfoRedactor:
    def __init__(self):
        self.red = RedactionService()

    def redact_info(self, info: InfoDTO, get_new_info: bool = False) -> pd.DataFrame:
        if get_new_info:
            upsert_orders(info.orders)
            upsert_sales(info.sales)

        orders_all_info = read_orders()
        sales_all_info = read_sales()

        if get_new_info:
            orders_all_info.to_excel(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}', index=False)
            upload_file(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}', REMOTE_PATH + YANDEX_DISC_ORDERS_FILE_NAME)

            sales_all_info.to_excel(f'{MAIN_DIR}{YANDEX_DISC_SALES_FILE_NAME}', index=False)
            upload_file(f'{MAIN_DIR}{YANDEX_DISC_SALES_FILE_NAME}', REMOTE_PATH + YANDEX_DISC_SALES_FILE_NAME)

        sales_main_info = self.red.get_sales_main_info(sales_all_info)
        orders_main_info = self.red.get_orders_main_info(orders_all_info)

        agg_table = self.red.merge_main_info(orders_main_info, sales_main_info)
        return agg_table