import pandas as pd

from config import MAIN_DIR
from yandex.config import BASE_ORDERS_FILE_NAME, BASE_RETURNS_FILE_NAME
from yandex.dto.info_yandex_dto import InfoYandexDTO
from yandex.dto.orders_columns import OrdersColumnsDTO
from yandex.services.redaction import RedactionService


class InfoRedactor:
    def __init__(self):
        self.red = RedactionService()
        self.orders_columns = OrdersColumnsDTO()

    def redact_info(self, info: InfoYandexDTO, get_new_info: bool = False) -> pd.DataFrame:
        if get_new_info:
            collections_list = [info.med_collection_1, info.med_collection_2,
                                info.med_collection_3, info.med_collection_4]
            yandex_collections_merged = collections_list[0]
            for coll in collections_list[1:]:
                yandex_collections_merged = self.red.merge_collections(yandex_collections_merged, coll)

            orders_with_brand = self.red.merge_with_med_collections(info.orders, yandex_collections_merged)
            returns_with_brand = self.red.merge_with_med_collections(info.returns, yandex_collections_merged)

            orders_all_info = self.red.merge_orders(info.all_orders, orders_with_brand)
            orders_all_info.to_excel(f'{MAIN_DIR}/{BASE_ORDERS_FILE_NAME}.xlsx', index=False)
            orders_main_info = self.red.orders_main_info(orders_all_info)

            returns_all_info = self.red.merge_returns(info.all_returns, returns_with_brand)
            returns_all_info.to_excel(f'{MAIN_DIR}/{BASE_RETURNS_FILE_NAME}.xlsx', index=False)
            returns_main_info = self.red.returns_main_info(returns_all_info)

            agg_table = self.red.merge_main_info(orders_main_info, returns_main_info)
            return agg_table
        else:
            orders_all_info = pd.read_excel(f'{MAIN_DIR}/{BASE_ORDERS_FILE_NAME}.xlsx')
            orders_main_info = self.red.orders_main_info(orders_all_info)

            returns_all_info = pd.read_excel(f'{MAIN_DIR}/{BASE_RETURNS_FILE_NAME}.xlsx')
            returns_main_info = self.red.returns_main_info(returns_all_info)

            agg_table = self.red.merge_main_info(orders_main_info, returns_main_info)
            return agg_table