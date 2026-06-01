from abc import ABC, abstractmethod
from dataclasses import asdict

import pandas as pd

from ozon.config import BASE_COLUMNS_NAME
from ozon.dto.orders_columns_dto import OrdersColumnsDTO
from ozon.dto.orders_main_info_dto import OrdersMainInfoColumnsDTO
from ozon.dto.returns_columns_dto import ReturnsColumnsDTO
from ozon.dto.returns_main_info_columns import ReturnsMainInfoColumnsDTO


class CorrectorStrategy(ABC):
    def __init__(self):
        self.orders_columns = OrdersColumnsDTO()
        self.returns_columns = ReturnsColumnsDTO()
        self.orders_main_info_columns = OrdersMainInfoColumnsDTO()
        self.returns_main_info_columns = ReturnsMainInfoColumnsDTO()

    @abstractmethod
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

class CorrOrdersStrategy(CorrectorStrategy):
    def correcting(self, orders: pd.DataFrame) -> pd.DataFrame:
        orders[self.orders_columns.brand] = orders[self.orders_columns.brand].str.strip()
        orders[self.orders_columns.brand] = orders[self.orders_columns.brand].replace('Marc Cony', 'MARC CONY')
        orders[self.orders_columns.brand] = orders[self.orders_columns.brand].replace('REDPIN', 'Red Pin')
        
        orders[self.orders_columns.created_at] = pd.to_datetime(orders[self.orders_columns.created_at])

        # 2. Создаём колонки: год, месяц, номер недели
        orders[self.orders_main_info_columns.market] = 'OZON'
        orders[self.orders_main_info_columns.year] = orders[self.orders_columns.created_at].dt.year
        orders[self.orders_main_info_columns.month] = orders[self.orders_columns.created_at].dt.month
        orders[self.orders_main_info_columns.week] = orders[self.orders_columns.created_at].dt.isocalendar().week

        orders['canceled_price'] = -orders[self.orders_columns.price].where(
            orders[self.orders_columns.status] == 'Отменён', 0
        )

        # 3. Группируем сначала по году, месяцу, неделе, бренду
        grouped = orders.groupby([self.orders_main_info_columns.market, self.orders_main_info_columns.year,
                                   self.orders_main_info_columns.month, self.orders_main_info_columns.week,
                                   self.orders_main_info_columns.brand]).agg(
            sum_orders=(self.orders_columns.price, 'sum'),  # количество заказов в группе
            total_orders=(self.orders_columns.quantity, 'sum'),  # количество заказов в группе
            returned=(self.orders_columns.status,  lambda x: x[x == 'Отменён'].count()),
            total_main_orders=(self.orders_columns.order_number, 'nunique'),
            returned_sum = ('canceled_price', 'sum'),
        ).reset_index()

        columns_name = [column for column in grouped.columns if column in BASE_COLUMNS_NAME]

        columns_rename = {k: BASE_COLUMNS_NAME.get(k) for k in columns_name}
        grouped.rename(columns_rename,
                  inplace=True,
                  axis=1)
        return grouped

class CorrReturnsStrategy(CorrectorStrategy):
    def correcting(self, returns: pd.DataFrame) -> pd.DataFrame:
        returns[self.returns_columns.brand] = returns[self.returns_columns.brand].str.strip()
        returns[self.returns_columns.brand] = returns[self.returns_columns.brand].replace('Marc Cony', 'MARC CONY')
        returns[self.returns_columns.brand] = returns[self.returns_columns.brand].replace('REDPIN', 'Red Pin')

        returns[self.returns_columns.return_date] = pd.to_datetime(returns[self.returns_columns.return_date])

        # 2. Создаём колонки: год, месяц, номер недели
        returns[self.returns_main_info_columns.market] = 'OZON'
        returns[self.returns_main_info_columns.year] = returns[self.returns_columns.return_date].dt.year
        returns[self.returns_main_info_columns.month] = returns[self.returns_columns.return_date].dt.month
        returns[self.returns_main_info_columns.week] = returns[self.returns_columns.return_date].dt.isocalendar().week

        returns[self.returns_columns.price] = -returns[self.returns_columns.price]

        # 3. Группируем сначала по году, месяцу, неделе, бренду
        grouped = returns.groupby([self.returns_main_info_columns.market, self.returns_main_info_columns.year,
                                   self.returns_main_info_columns.month, self.returns_main_info_columns.week,
                                   self.returns_main_info_columns.brand]).agg(
            returned=(self.returns_columns.quantity, 'sum'),
            returned_sum=(self.returns_columns.price, 'sum'),
        ).reset_index()

        columns_name = [column for column in grouped.columns if column in BASE_COLUMNS_NAME]

        columns_rename = {k: BASE_COLUMNS_NAME.get(k) for k in columns_name}
        grouped.rename(columns_rename,
                  inplace=True,
                  axis=1)
        return grouped