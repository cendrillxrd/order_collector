import pandas as pd

from config import MAIN_DIR
from wb.config import BASE_ORDERS_FILE_NAME, BASE_SALES_FILE_NAME
from wb.dto.info_dto import InfoDTO
from wb.dto.orders_columns_dto import OrdersColumnsDTO
from wb.dto.sales_columns_dto import SalesColumnsDTO
from wb.services.red import RedactionService


class InfoRedactor:
    def __init__(self):
        self.red = RedactionService()
        self.orders_columns = OrdersColumnsDTO()
        self.sales_columns = SalesColumnsDTO()

    def redact_info(self, info: InfoDTO, get_new_info: bool = False) -> pd.DataFrame:
        if get_new_info:
            sales_all_info = self.red.merge_sales(info.all_sales, info.sales)
            sales_all_info.to_excel(f'{MAIN_DIR}/{BASE_SALES_FILE_NAME}.xlsx', index=False)

            orders_all_info = self.red.merge_orders(info.all_orders, info.orders)
            orders_all_info.to_excel(f'{MAIN_DIR}/{BASE_ORDERS_FILE_NAME}.xlsx', index=False)

            sales_main_info = self.red.sales_main_info(sales_all_info)
            orders_main_info = self.red.orders_main_info(orders_all_info)

            agg_table = self.red.merge_main_info(orders_main_info, sales_main_info)
            return agg_table
        else:
            sales_all_info = pd.read_excel(f'{MAIN_DIR}/{BASE_SALES_FILE_NAME}.xlsx')

            orders_all_info = pd.read_excel(f'{MAIN_DIR}/{BASE_ORDERS_FILE_NAME}.xlsx')

            sales_main_info = self.red.sales_main_info(sales_all_info)
            orders_main_info = self.red.orders_main_info(orders_all_info)

            agg_table = self.red.merge_main_info(orders_main_info, sales_main_info)
            return agg_table