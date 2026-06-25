from abc import ABC, abstractmethod

import pandas as pd

from yandex.yandex_config import BASE_MAIN_COLUMNS_NAME
from yandex.dto.orders_columns import OrdersColumnsDTO
from yandex.dto.orders_main_info_dto import OrdersMainInfoColumnsDTO
from yandex.dto.returned_columns_dto import ReturnedColumnsDTO
from yandex.dto.returns_main_info_columns import ReturnsMainInfoColumnsDTO


class CorrectStrategy(ABC):
    def __init__(self):
        self.orders_columns = OrdersColumnsDTO()
        self.returns_columns = ReturnedColumnsDTO()
        self.orders_main_info_columns = OrdersMainInfoColumnsDTO()
        self.returns_main_info_columns = ReturnsMainInfoColumnsDTO()

    @abstractmethod
    def do_correct(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        pass

class CorrOrdersStrategy(CorrectStrategy):
    def do_correct(self, orders: pd.DataFrame, **kwargs) -> pd.DataFrame:
        orders[self.orders_columns.brand] = orders[self.orders_columns.brand].str.strip()
        orders[self.orders_columns.brand] = orders[self.orders_columns.brand].replace('Marc Cony', 'MARC CONY')

        orders[self.orders_columns.creation_date] = pd.to_datetime(orders[self.orders_columns.creation_date])

        # 2. Создаём колонки: год, месяц, номер недели
        orders[self.orders_main_info_columns.market] = 'YANDEX'
        orders[self.orders_main_info_columns.year] = orders[self.orders_columns.creation_date].dt.year
        orders[self.orders_main_info_columns.month] = orders[self.orders_columns.creation_date].dt.month
        orders[self.orders_main_info_columns.week] = orders[self.orders_columns.creation_date].dt.isocalendar().week

        orders['canceled_price'] = -orders[self.orders_columns.price].where(
            orders[self.orders_columns.status] == 'CANCELLED', 0)

        # 3. Группируем сначала по году, месяцу, неделе, бренду
        grouped = orders.groupby([self.orders_main_info_columns.market, self.orders_main_info_columns.year,
                                   self.orders_main_info_columns.month, self.orders_main_info_columns.week,
                                   self.orders_main_info_columns.brand]).agg(
            sum_orders=(self.orders_columns.price, 'sum'),  # количество заказов в группе
            sum_shipment=(self.orders_columns.price, 'sum'),  # количество заказов в группе
            total_orders=(self.orders_columns.order_id, 'count'),  # количество заказов в группе
            returned=(self.orders_columns.status, lambda x: x[x == 'CANCELLED'].count()),
            total_main_orders=(self.orders_columns.order_id, 'nunique'),
            returned_sum=('canceled_price', 'sum'),
        ).reset_index()

        columns_name = [column for column in grouped.columns if column in BASE_MAIN_COLUMNS_NAME]

        columns_rename = {k: BASE_MAIN_COLUMNS_NAME.get(k) for k in columns_name}
        grouped.rename(columns_rename,
                  inplace=True,
                  axis=1)

        return grouped

class CorrReturnsStrategy(CorrectStrategy):
    def do_correct(self, returns: pd.DataFrame, **kwargs) -> pd.DataFrame:
        returns[self.returns_columns.brand] = returns[self.returns_columns.brand].str.strip()
        returns[self.returns_columns.brand] = returns[self.returns_columns.brand].replace('Marc Cony', 'MARC CONY')

        returns[self.returns_columns.creation_date] = pd.to_datetime(returns[self.returns_columns.creation_date])

        # 2. Создаём колонки: год, месяц, номер недели
        returns[self.returns_main_info_columns.market] = 'YANDEX'
        returns[self.returns_main_info_columns.year] = returns[self.returns_columns.creation_date].dt.year
        returns[self.returns_main_info_columns.month] = returns[self.returns_columns.creation_date].dt.month
        returns[self.returns_main_info_columns.week] = returns[self.returns_columns.creation_date].dt.isocalendar().week

        returns[self.returns_columns.amount] = -returns[self.returns_columns.amount]

        # 3. Группируем сначала по году, месяцу, неделе, бренду
        grouped = returns.groupby([self.returns_main_info_columns.market, self.returns_main_info_columns.year,
                                   self.returns_main_info_columns.month, self.returns_main_info_columns.week,
                                   self.returns_main_info_columns.brand]).agg(
            returned=(self.returns_columns.count, 'sum'),
            returned_sum=(self.returns_columns.amount, 'sum'),
        ).reset_index()

        columns_name = [column for column in grouped.columns if column in BASE_MAIN_COLUMNS_NAME]

        columns_rename = {k: BASE_MAIN_COLUMNS_NAME.get(k) for k in columns_name}
        grouped.rename(columns_rename,
                  inplace=True,
                  axis=1)

        return grouped