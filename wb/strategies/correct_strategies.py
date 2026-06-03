from abc import ABC, abstractmethod

import pandas as pd

from wb.config import BASE_MAIN_COLUMNS_NAME
from wb.dto.orders_columns_dto import OrdersColumnsDTO
from wb.dto.orders_main_info_dto import OrdersMainInfoColumnsDTO
from wb.dto.sales_columns_dto import SalesColumnsDTO
from wb.dto.sales_main_info_dto import SalesMainInfoColumnsDTO


class CorrectorStrategy(ABC):
    def __init__(self):
        self.orders_columns = OrdersColumnsDTO()
        self.sales_columns = SalesColumnsDTO()
        self.orders_main_info_columns = OrdersMainInfoColumnsDTO()
        self.sales_main_info_columns = SalesMainInfoColumnsDTO()
    @abstractmethod
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

class CorrOrdersStrategy(CorrectorStrategy):
    def correcting(self, orders: pd.DataFrame) -> pd.DataFrame:
        orders[self.orders_columns.brand] = orders[self.orders_columns.brand].str.strip()
        orders[self.orders_columns.brand] = orders[self.orders_columns.brand].replace('Marc Cony', 'MARC CONY')
        orders[self.orders_columns.brand] = orders[self.orders_columns.brand].replace('PEPE JEANS LONDON', 'Pepe Jeans')

        orders[self.orders_columns.date] = pd.to_datetime(orders[self.orders_columns.date])

        # 2. Создаём колонки: год, месяц, номер недели
        orders[self.orders_main_info_columns.market] = 'WB'
        orders[self.orders_main_info_columns.year] = orders[self.orders_columns.date].dt.year
        orders[self.orders_main_info_columns.month] = orders[self.orders_columns.date].dt.month
        orders[self.orders_main_info_columns.week] = orders[self.orders_columns.date].dt.isocalendar().week  # ISO недели (1-53)
        orders[self.orders_columns.price_with_discount] = orders[self.orders_columns.totalPrice] * (1 - orders[self.orders_columns.discountPercent] / 100)# ISO недели (1-53)

        orders['returned_value'] = (
                orders[self.orders_columns.price_with_discount]
                * orders[self.orders_columns.isCanceled]
                * -1
        )
        orders['order'] = orders['ID заказа'].apply(lambda x: max(str(x).split('.'), key=len))

        # 3. Группируем сначала по году, месяцу, неделе, бренду
        grouped = orders.groupby([self.orders_main_info_columns.market, self.orders_main_info_columns.year,
                                   self.orders_main_info_columns.month, self.orders_main_info_columns.week,
                                   self.orders_main_info_columns.brand]).agg(
            sum_orders=(self.orders_columns.price_with_discount, 'sum'),  # количество заказов в группе
            sum_shipment=(self.orders_columns.price_with_discount, 'sum'),  # количество заказов в группе
            total_orders=(self.orders_columns.totalPrice, 'count'),  # количество заказов в группе
            returned=(self.orders_columns.isCanceled, 'sum'),
            returned_sum=('returned_value', 'sum'),
            total_main_orders=('order', 'nunique')
        ).reset_index()

        columns_name = [column for column in grouped.columns if column in BASE_MAIN_COLUMNS_NAME]

        columns_rename = {k: BASE_MAIN_COLUMNS_NAME.get(k) for k in columns_name}
        grouped.rename(columns_rename,
                  inplace=True,
                  axis=1)
        return grouped
    
class CorrSalesStrategy(CorrectorStrategy):
    def correcting(self, sales: pd.DataFrame) -> pd.DataFrame:
        sales[self.sales_columns.brand] = sales[self.sales_columns.brand].str.strip()
        sales[self.sales_columns.brand] = sales[self.sales_columns.brand].replace('Marc Cony', 'MARC CONY')
        sales[self.orders_columns.brand] = sales[self.orders_columns.brand].replace('PEPE JEANS LONDON', 'Pepe Jeans')

        sales[self.sales_columns.date] = pd.to_datetime(sales[self.sales_columns.date])

        # 2. Создаём колонки: год, месяц, номер недели
        sales[self.sales_main_info_columns.market] = 'WB'
        sales[self.sales_main_info_columns.year] = sales[self.sales_columns.date].dt.year
        sales[self.sales_main_info_columns.month] = sales[self.sales_columns.date].dt.month
        sales[self.sales_main_info_columns.week] = sales[self.sales_columns.date].dt.isocalendar().week  # ISO недели (1-53)

        # 3. Группируем сначала по году, месяцу, неделе, бренду
        grouped = sales.groupby([self.sales_main_info_columns.market,
                                 self.sales_main_info_columns.year,
                                 self.sales_main_info_columns.month,
                                 self.sales_main_info_columns.week,
                                 self.sales_main_info_columns.brand]).agg(
            returned_sum=(self.sales_columns.priceWithDisc, lambda x: x[x < 0].sum()),
            returned=(self.sales_columns.priceWithDisc, lambda x: x[x < 0].count()),
        ).reset_index()

        columns_name = [column for column in grouped.columns if column in BASE_MAIN_COLUMNS_NAME]

        columns_rename = {k: BASE_MAIN_COLUMNS_NAME.get(k) for k in columns_name}
        grouped.rename(columns_rename,
                       inplace=True,
                       axis=1)
        return grouped