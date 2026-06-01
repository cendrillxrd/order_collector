from abc import ABC, abstractmethod

import pandas as pd

from lamoda.config import ON_THE_WAY_GOODS_SHIPS_STATUS, ON_THE_WAY_SHIP_STATUS
from lamoda.dto.all_agg_info_dto import AllAggInfoColumnsDTO
from lamoda.dto.columns_main_dto import ColumnsMainDTO

columns_main = ColumnsMainDTO()
all_agg_info_columns = AllAggInfoColumnsDTO()


class MergeStrategies(ABC):
    @abstractmethod
    def merge(self, *args) -> pd.DataFrame:
        pass

# class MergeCollections(MergeStrategies):
#     def __init__(self, merge_on: str = columns_main.supplier_parent_sku):
#         self.merge_on = merge_on
#
#     def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
#         merged_df = pd.concat([df1, df2], ignore_index=True)
#         return merged_df


class MergeOrders(MergeStrategies):
    def __init__(self, merge_on: tuple = (columns_main.id, columns_main.sku)):
        self.merge_on = merge_on

    def _add_position_counter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Добавляет временный счетчик позиций"""
        df = df.copy()
        df['_temp_position'] = df.groupby(list(self.merge_on)).cumcount()
        return df

    def merge(self, orders_main: pd.DataFrame, orders_new: pd.DataFrame) -> pd.DataFrame:
        # Добавляем временный счетчик
        orders_main_with_pos = self._add_position_counter(orders_main)
        orders_new_with_pos = self._add_position_counter(orders_new)

        # Полный список для индекса
        full_merge_on = list(self.merge_on) + ['_temp_position']

        # Устанавливаем индекс
        df_main_indexed = orders_main_with_pos.set_index(full_merge_on)
        df_additional_indexed = orders_new_with_pos.set_index(full_merge_on)

        # Обновляем данные
        result = df_additional_indexed.combine_first(df_main_indexed)

        # Сбрасываем индекс
        result = result.reset_index()

        # Удаляем временную колонку
        result = result.drop('_temp_position', axis=1)

        # Сортируем
        result.sort_values(columns_main.created_at, inplace=True, ascending=True)

        return result


class MergeOrdersBrand(MergeStrategies):
    def __init__(self, merge_on: str = columns_main.sku):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged = pd.merge(df1, df2, on=columns_main.sku, how='left')
        return merged

class MergeOrdersWithReturnsStrategy(MergeStrategies):
    def __init__(self, merge_on=[all_agg_info_columns.market, all_agg_info_columns.year, all_agg_info_columns.month,
                                 all_agg_info_columns.week, all_agg_info_columns.brand]):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged = pd.concat([df1, df2]).groupby(self.merge_on, as_index=False).sum()
        return merged