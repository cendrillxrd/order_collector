import pandas as pd

from config import MAIN_DIR
from ozon.config import BASE_ORDERS_FILE_NAME, EXCEL_FILE_NAME, BASE_RETURNS_FILE_NAME
from ozon.dto.info_dto import InfoDTO
from ozon.dto.orders_columns_dto import OrdersColumnsDTO
from ozon.services.red import RedactionService


class InfoRedactor:
    def __init__(self):
        self.red = RedactionService()
        self.orders_columns = OrdersColumnsDTO()

    def redact_info(self, info: InfoDTO, get_new_info: bool = False) -> pd.DataFrame:
        if get_new_info:
            orders_with_brand = self.red.merge_with_brand(info.orders, info.cards_info)
            returns_with_brand = self.red.merge_with_brand(info.returns, info.cards_info)

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