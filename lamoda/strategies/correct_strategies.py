from abc import ABC, abstractmethod
from dataclasses import asdict

import pandas as pd

from lamoda.config import BASE_MAIN_COLUMNS_NAME
from lamoda.dto.columns_main_dto import ColumnsMainDTO
from lamoda.dto.orders_main_info_dto import OrdersMainInfoColumnsDTO
from lamoda.dto.returns_main_info_columns import ReturnsMainInfoColumnsDTO
from lamoda.utils.date_helper import filter_until_last_sunday


class CorrectorStrategy(ABC):
    def __init__(self):
        self.orders_columns = ColumnsMainDTO()
        self.returns_main_info_columns = ReturnsMainInfoColumnsDTO()
        self.orders_main_info_columns = OrdersMainInfoColumnsDTO()

    @abstractmethod
    def correcting(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        pass
class CorrOrdersStrategy(CorrectorStrategy):
    def correcting(self, orders: pd.DataFrame, **kwargs) -> pd.DataFrame:
        orders[self.orders_columns.brand] = orders[self.orders_columns.brand].str.strip()
        orders[self.orders_columns.brand] = orders[self.orders_columns.brand].replace('Marc Cony', 'MARC CONY')

        orders[self.orders_columns.created_at] = pd.to_datetime(orders[self.orders_columns.created_at])

        # # 2. Создаём колонки: год, месяц, номер недели
        orders[self.orders_main_info_columns.market] = 'LAMODA'
        orders[self.orders_main_info_columns.year] = orders[self.orders_columns.created_at].dt.year
        orders[self.orders_main_info_columns.month] = orders[self.orders_columns.created_at].dt.month
        orders[self.orders_main_info_columns.week] = orders[self.orders_columns.created_at].dt.isocalendar().week

        returned_statuses = ['Returned', 'Canceled', 'Not delivered', 'Not bought']

        orders['canceled_price'] = -orders[self.orders_columns.partner_agreed_price].where(
            orders[self.orders_columns.status_product].isin(returned_statuses), 0)

        # 3. Группируем сначала по году, месяцу, неделе, бренду
        grouped = orders.groupby([self.orders_main_info_columns.market, self.orders_main_info_columns.year,
                                   self.orders_main_info_columns.month, self.orders_main_info_columns.week,
                                   self.orders_main_info_columns.brand]).agg(
            sum_orders=(self.orders_columns.partner_agreed_price, 'sum'),
            total_orders=(self.orders_columns.id, 'count'),
            returned=(self.orders_columns.status_product, lambda x: x[x.isin(returned_statuses)].count()),
            total_main_orders=(self.orders_columns.id, 'nunique'),
            returned_sum=('canceled_price', 'sum'),
        ).reset_index()

        columns_name = [column for column in grouped.columns if column in BASE_MAIN_COLUMNS_NAME]

        columns_rename = {k: BASE_MAIN_COLUMNS_NAME.get(k) for k in columns_name}
        grouped.rename(columns_rename,
                  inplace=True,
                  axis=1)
        return grouped

class CorrReturnsStrategy(CorrectorStrategy):
    def correcting(self, returns: pd.DataFrame, **kwargs) -> pd.DataFrame:
        returns[self.orders_columns.brand] = returns[self.orders_columns.brand].str.strip()
        returns[self.orders_columns.brand] = returns[self.orders_columns.brand].replace('Marc Cony', 'MARC CONY')

        returns[self.orders_columns.updated_at] = pd.to_datetime(returns[self.orders_columns.updated_at])
        returns = filter_until_last_sunday(returns, self.orders_columns.updated_at)

        # 2. Создаём колонки: год, месяц, номер недели
        returns[self.returns_main_info_columns.market] = 'LAMODA'
        returns[self.returns_main_info_columns.year] = returns[self.orders_columns.updated_at].dt.year
        returns[self.returns_main_info_columns.month] = returns[self.orders_columns.updated_at].dt.month
        returns[self.returns_main_info_columns.week] = returns[self.orders_columns.updated_at].dt.isocalendar().week

        returned_statuses = ['Refunded', 'Refund necessary', 'Ready to refund']

        returns['canceled_price'] = -returns[self.orders_columns.partner_agreed_price].where(
            returns[self.orders_columns.status_product].isin(returned_statuses), 0)

        # 3. Группируем сначала по году, месяцу, неделе, бренду
        grouped = returns.groupby([self.returns_main_info_columns.market, self.returns_main_info_columns.year,
                                   self.returns_main_info_columns.month, self.returns_main_info_columns.week,
                                   self.returns_main_info_columns.brand]).agg(
            returned=(self.orders_columns.status_product, lambda x: x[x.isin(returned_statuses)].count()),
            returned_sum=('canceled_price', 'sum'),
        ).reset_index()

        columns_name = [column for column in grouped.columns if column in BASE_MAIN_COLUMNS_NAME]

        columns_rename = {k: BASE_MAIN_COLUMNS_NAME.get(k) for k in columns_name}
        grouped.rename(columns_rename,
                  inplace=True,
                  axis=1)

        return grouped

class CorrBrandOrders(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        columns_to_int = [
                          self.orders_columns.total_discount,
                          self.orders_columns.sale_price,
                          self.orders_columns.paid_price,
                          self.orders_columns.base_price,
                          self.orders_columns.coupon_discount,
                          self.orders_columns.loyalty_discount,
                          self.orders_columns.partner_agreed_discount,
                          self.orders_columns.platform_discounts,
                          self.orders_columns.other_discounts,
                          self.orders_columns.partner_agreed_price,
                          ]
        for col in columns_to_int:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(int)
        df = df[asdict(self.orders_columns).values()].copy()
        return df
