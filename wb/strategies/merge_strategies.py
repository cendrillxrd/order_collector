from abc import ABC, abstractmethod
from dataclasses import asdict

import pandas as pd

from wb.dto.all_agg_info_dto import AllAggInfoColumnsDTO
from wb.dto.orders_columns_dto import OrdersColumnsDTO
from wb.dto.sales_columns_dto import SalesColumnsDTO

orders_columns = OrdersColumnsDTO()
sales_columns = SalesColumnsDTO()
all_agg_info_columns = AllAggInfoColumnsDTO()

class MergeStrategies(ABC):
    @abstractmethod
    def merge(self, *args) -> pd.DataFrame:
        pass

class MergeOrdersInfoStrategy(MergeStrategies):
    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame):
        df1 = df1.set_index(orders_columns.srid)
        df2 = df2.set_index(orders_columns.srid)

        df_updated = df2.combine_first(df1).reset_index()
        df_updated = df_updated[
            [col for col in asdict(orders_columns).values() if col in df_updated.columns]].copy()
        df_updated[orders_columns.date] = pd.to_datetime(df_updated[orders_columns.date])
        df_updated.sort_values(by=orders_columns.date, inplace=True)
        return df_updated

class MergeSalesInfoStrategy(MergeStrategies):
    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame):
        df_merged_sales = pd.concat([df1, df2[df1.columns]], ignore_index=True)
        df_merged_sales[sales_columns.date] = pd.to_datetime(df_merged_sales[sales_columns.date])

        df_merged_sales.sort_values(by=sales_columns.date, inplace=True)
        return df_merged_sales

class MergeOrdersWithSalesStrategy(MergeStrategies):
    def __init__(self, merge_on = [all_agg_info_columns.market, all_agg_info_columns.year, all_agg_info_columns.month, all_agg_info_columns.week, all_agg_info_columns.brand]):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged = pd.concat([df1, df2]).groupby(self.merge_on, as_index=False).sum()
        return merged