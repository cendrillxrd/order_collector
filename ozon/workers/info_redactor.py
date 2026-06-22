import pandas as pd

from config import MAIN_DIR, REMOTE_PATH
from ozon.ozon_config import YANDEX_DISC_RETURNS_FILE_NAME, YANDEX_DISC_ORDERS_FILE_NAME, LOCAL_RETURNS_PATH, LOCAL_ORDERS_PATH
from ozon.dto.info_dto import InfoDTO
from ozon.dto.orders_columns_dto import OrdersColumnsDTO
from ozon.repositories.db_repository import upsert_ozon_orders, upsert_ozon_returns
from ozon.services.red import RedactionService
from yandex_disk import download_file, upload_file


class InfoRedactor:
    def __init__(self):
        self.red = RedactionService()
        self.orders_columns = OrdersColumnsDTO()

    def redact_info(self, info: InfoDTO, get_new_info: bool = False) -> pd.DataFrame:
        if get_new_info:
            upsert_ozon_orders(info.orders)
            upsert_ozon_returns(info.returns)

            orders_with_brand = self.red.merge_with_brand(info.orders, info.cards_info)
            returns_with_brand = self.red.merge_with_brand(info.returns, info.cards_info)

            orders_all_info = self.red.merge_orders(info.all_orders, orders_with_brand)
            orders_all_info.to_excel(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}', index=False)
            upload_file(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}', REMOTE_PATH + YANDEX_DISC_ORDERS_FILE_NAME)
            orders_main_info = self.red.orders_main_info(orders_all_info)

            returns_all_info = self.red.merge_returns(info.all_returns, returns_with_brand)
            returns_all_info.to_excel(f'{MAIN_DIR}{YANDEX_DISC_RETURNS_FILE_NAME}', index=False)
            upload_file(f'{MAIN_DIR}{YANDEX_DISC_RETURNS_FILE_NAME}', REMOTE_PATH + YANDEX_DISC_RETURNS_FILE_NAME)
            returns_main_info = self.red.returns_main_info(returns_all_info)

            agg_table = self.red.merge_main_info(orders_main_info, returns_main_info)
            return agg_table
        else:
            download_file(REMOTE_PATH + YANDEX_DISC_RETURNS_FILE_NAME, LOCAL_RETURNS_PATH)
            download_file(REMOTE_PATH + YANDEX_DISC_ORDERS_FILE_NAME, LOCAL_ORDERS_PATH)

            orders_all_info = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}')
            orders_main_info = self.red.orders_main_info(orders_all_info)

            returns_all_info = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_RETURNS_FILE_NAME}')
            returns_main_info = self.red.returns_main_info(returns_all_info)

            agg_table = self.red.merge_main_info(orders_main_info, returns_main_info)
            return agg_table