import pandas as pd

from config import MAIN_DIR, REMOTE_PATH
from ozon.ozon_config import YANDEX_DISC_RETURNS_FILE_NAME, YANDEX_DISC_ORDERS_FILE_NAME
from ozon.dto.info_dto import InfoDTO
from ozon.dto.orders_columns_dto import OrdersColumnsDTO
from ozon.repositories.db_repository import upsert_ozon_orders, upsert_ozon_returns, read_ozon_orders, read_ozon_returns
from ozon.services.red import RedactionService
from yandex_disk import upload_file


class InfoRedactor:
    def __init__(self):
        self.red = RedactionService()
        self.orders_columns = OrdersColumnsDTO()

    def redact_info(self, info: InfoDTO, get_new_info: bool = False) -> pd.DataFrame:
        if get_new_info:
            orders_with_brand = self.red.merge_with_brand(info.orders, info.cards_info)
            returns_with_brand = self.red.merge_with_brand(info.returns, info.cards_info)
            upsert_ozon_orders(orders_with_brand)
            upsert_ozon_returns(returns_with_brand)

        orders_all_info = read_ozon_orders()
        returns_all_info = read_ozon_returns()

        if get_new_info:
            orders_all_info.to_excel(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}', index=False)
            upload_file(f'{MAIN_DIR}{YANDEX_DISC_ORDERS_FILE_NAME}', REMOTE_PATH + YANDEX_DISC_ORDERS_FILE_NAME)

            returns_all_info.to_excel(f'{MAIN_DIR}{YANDEX_DISC_RETURNS_FILE_NAME}', index=False)
            upload_file(f'{MAIN_DIR}{YANDEX_DISC_RETURNS_FILE_NAME}', REMOTE_PATH + YANDEX_DISC_RETURNS_FILE_NAME)

        orders_main_info = self.red.orders_main_info(orders_all_info)
        returns_main_info = self.red.returns_main_info(returns_all_info)

        agg_table = self.red.merge_main_info(orders_main_info, returns_main_info)
        return agg_table