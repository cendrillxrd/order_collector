from abc import ABC, abstractmethod

import pandas as pd

from wb.utils.corr_helpers import correct_columns_name
from wb.wb_config import BASE_MAIN_COLUMNS_NAME, MARKET_NAME
from wb.dto.orders_columns_dto import OrdersColumnsDTO
from wb.dto.orders_main_info_dto import OrdersMainInfoColumnsDTO
from wb.dto.sales_columns_dto import SalesColumnsDTO
from wb.dto.sales_main_info_dto import SalesMainInfoColumnsDTO


class CorrectStrategy(ABC):
    def __init__(self):
        self.orders_columns = OrdersColumnsDTO()
        self.sales_columns = SalesColumnsDTO()
        self.orders_main_info_columns = OrdersMainInfoColumnsDTO()
        self.sales_main_info_columns = SalesMainInfoColumnsDTO()

    @abstractmethod
    def do_correct(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        pass

class CorrOrdersStrategy(CorrectStrategy):
    def do_correct(self, orders: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        orders[self.orders_columns.brand] = orders[self.orders_columns.brand].str.strip()

        orders[self.orders_columns.date] = pd.to_datetime(orders[self.orders_columns.date])

        orders[self.orders_main_info_columns.market] = MARKET_NAME
        orders[self.orders_main_info_columns.year] = orders[self.orders_columns.date].dt.year
        orders[self.orders_main_info_columns.month] = orders[self.orders_columns.date].dt.month
        orders[self.orders_main_info_columns.week] = orders[self.orders_columns.date].dt.isocalendar().week

        orders['returned_value'] = (
                orders[self.orders_columns.price_with_discount] * orders[self.orders_columns.isCanceled] * -1
        )
        orders['order'] = orders['ID заказа'].apply(lambda x: max(str(x).split('.'), key=len))

        grouped = orders.groupby([self.orders_main_info_columns.market, self.orders_main_info_columns.year,
                                   self.orders_main_info_columns.month, self.orders_main_info_columns.week,
                                   self.orders_main_info_columns.brand]).agg(
            sum_orders=(self.orders_columns.price_with_discount, 'sum'),
            sum_shipment=(self.orders_columns.price_with_discount, 'sum'),
            total_orders=(self.orders_columns.totalPrice, 'count'),
            returned=(self.orders_columns.isCanceled, 'sum'),
            returned_sum=('returned_value', 'sum'),
            total_main_orders=('order', 'nunique')
        ).reset_index()

        grouped = correct_columns_name(grouped, BASE_MAIN_COLUMNS_NAME)
        return grouped
    
class CorrSalesStrategy(CorrectStrategy):
    def do_correct(self, sales: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        sales[self.sales_columns.brand] = sales[self.sales_columns.brand].str.strip()

        sales[self.sales_columns.date] = pd.to_datetime(sales[self.sales_columns.date])

        sales[self.sales_main_info_columns.market] = MARKET_NAME
        sales[self.sales_main_info_columns.year] = sales[self.sales_columns.date].dt.year
        sales[self.sales_main_info_columns.month] = sales[self.sales_columns.date].dt.month
        sales[self.sales_main_info_columns.week] = sales[self.sales_columns.date].dt.isocalendar().week

        grouped = sales.groupby([self.sales_main_info_columns.market,
                                 self.sales_main_info_columns.year,
                                 self.sales_main_info_columns.month,
                                 self.sales_main_info_columns.week,
                                 self.sales_main_info_columns.brand]).agg(
            returned_sum=(self.sales_columns.priceWithDisc, lambda x: x[x < 0].sum()),
            returned=(self.sales_columns.priceWithDisc, lambda x: x[x < 0].count()),
        ).reset_index()

        grouped = correct_columns_name(grouped, BASE_MAIN_COLUMNS_NAME)
        return grouped