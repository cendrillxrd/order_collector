from abc import ABC, abstractmethod
from dataclasses import asdict

import pandas as pd

from wb.dto.all_agg_info_dto import AllAggInfoColumnsDTO
from wb.dto.orders_columns_dto import OrdersColumnsDTO
from wb.dto.sales_columns_dto import SalesColumnsDTO


class MergeStrategy(ABC):
    def __init__(self):
        self.orders_columns = OrdersColumnsDTO()
        self.sales_columns = SalesColumnsDTO()
        self.all_agg_info_columns = AllAggInfoColumnsDTO()

    @abstractmethod
    def do_merge(self, df1: pd.DataFrame, df2: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        pass

class MergeOrdersInfoStrategy(MergeStrategy):
    def do_merge(self, df1: pd.DataFrame, df2: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        df1 = df1.set_index(self.orders_columns.srid)
        df2 = df2.set_index(self.orders_columns.srid)

        df_merged_orders = df2.combine_first(df1).reset_index()
        df_merged_orders = df_merged_orders[[col for col in asdict(self.orders_columns).values() if col in df_merged_orders.columns]].copy()
        df_merged_orders[self.orders_columns.date] = pd.to_datetime(df_merged_orders[self.orders_columns.date])
        df_merged_orders[self.orders_columns.lastChangeDate] = pd.to_datetime(df_merged_orders[self.orders_columns.lastChangeDate])
        df_merged_orders.sort_values(by=self.orders_columns.date, inplace=True)
        return df_merged_orders

class MergeSalesInfoStrategy(MergeStrategy):
    def do_merge(self, df1: pd.DataFrame, df2: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        df1 = df1.set_index(self.sales_columns.srid)
        df2 = df2.set_index(self.sales_columns.srid)

        df_merged_sales = df2.combine_first(df1).reset_index()
        df_merged_sales = df_merged_sales[[col for col in asdict(self.sales_columns).values() if col in df_merged_sales.columns]].copy()
        df_merged_sales[self.sales_columns.date] = pd.to_datetime(df_merged_sales[self.sales_columns.date])
        df_merged_sales[self.orders_columns.lastChangeDate] = pd.to_datetime(df_merged_sales[self.orders_columns.lastChangeDate])
        df_merged_sales.sort_values(by=self.sales_columns.date, inplace=True)
        return df_merged_sales

class MergeOrdersWithSalesStrategy(MergeStrategy):
    def __init__(self):
        super().__init__()
        self.merge_on = [self.all_agg_info_columns.market,
                         self.all_agg_info_columns.year,
                         self.all_agg_info_columns.month,
                         self.all_agg_info_columns.week,
                         self.all_agg_info_columns.brand]

    def do_merge(self, df1: pd.DataFrame, df2: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        merged = pd.concat([df1, df2]).groupby(self.merge_on, as_index=False).sum()
        return merged