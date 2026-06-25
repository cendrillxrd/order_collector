import pandas as pd
from functools import reduce
from config import MAIN_DIR, REMOTE_PATH
from yandex.yandex_config import YANDEX_DISC_RETURNS_FILE_NAME, YANDEX_DISC_ORDERS_FILE_NAME, LOCAL_RETURNS_PATH, LOCAL_ORDERS_PATH
from yandex.dto.info_yandex_dto import InfoYandexDTO
from yandex.dto.orders_columns import OrdersColumnsDTO
from yandex.repositories.db_repository import upsert_yandex_orders, upsert_yandex_returns
from yandex.services.redaction_service import RedactionService
from yandex_disk import download_file, upload_file


class InfoRedactor:
    def __init__(self):
        self.red = RedactionService()
        self.orders_columns = OrdersColumnsDTO()

    def redact_info(self, info: InfoYandexDTO, get_new_info: bool = False) -> pd.DataFrame:
        if get_new_info:
            yandex_collections_merged = reduce(
                self.red.merge_collections,
                info.med_collections
            )

            orders_with_brand = self.red.merge_with_med_collections(info.orders, yandex_collections_merged)
            returns_with_brand = self.red.merge_with_med_collections(info.returns, yandex_collections_merged)

            upsert_yandex_orders(orders_with_brand)
            upsert_yandex_returns(returns_with_brand)

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