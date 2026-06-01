from abc import ABC, abstractmethod
from dataclasses import asdict

import pandas as pd

from ozon.dto.all_agg_info_dto import AllAggInfoColumnsDTO
from ozon.dto.orders_columns_dto import OrdersColumnsDTO
from ozon.dto.returns_columns_dto import ReturnsColumnsDTO

orders_columns = OrdersColumnsDTO()
returns_columns = ReturnsColumnsDTO()
all_agg_info_columns = AllAggInfoColumnsDTO()

class MergeStrategies(ABC):
    @abstractmethod
    def merge(self, *args) -> pd.DataFrame:
        pass

class MergeWithBrandStrategy(MergeStrategies):
    def __init__(self, merge_on: str = orders_columns.sku):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        df1[self.merge_on] = df1[self.merge_on].astype(str)
        df2[self.merge_on] = df2[self.merge_on].astype(str)
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df


class MergeOrdersInfoStrategy(MergeStrategies):
    def __init__(self, merge_on: tuple = (orders_columns.posting_number, orders_columns.offer_id)):
        self.merge_on = merge_on

    def _add_position_counter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Добавляет временный счетчик позиций для различения дубликатов"""
        df = df.copy()
        df['_temp_position'] = df.groupby(list(self.merge_on)).cumcount()
        return df

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame):
        df1[returns_columns.posting_number] = df1[returns_columns.posting_number].astype(str)
        df1[returns_columns.offer_id] = df1[returns_columns.offer_id].astype(str)
        df2[returns_columns.posting_number] = df2[returns_columns.posting_number].astype(str)
        df2[returns_columns.offer_id] = df2[returns_columns.offer_id].astype(str)
        # Добавляем временный счетчик для обработки дубликатов
        df1_with_pos = self._add_position_counter(df1)
        df2_with_pos = self._add_position_counter(df2)

        # Полный список для индекса (включая временный счетчик)
        full_merge_on = list(self.merge_on) + ['_temp_position']

        # Устанавливаем мультииндекс
        df1_indexed = df1_with_pos.set_index(full_merge_on)
        df2_indexed = df2_with_pos.set_index(full_merge_on)

        # Объединяем с приоритетом новых данных (df2)
        df_updated = df2_indexed.combine_first(df1_indexed)

        # Сбрасываем индекс
        df_updated = df_updated.reset_index()

        # Удаляем временную колонку
        df_updated = df_updated.drop('_temp_position', axis=1)

        # Фильтруем только нужные колонки (как в оригинале)
        df_updated = df_updated[
            [col for col in asdict(orders_columns).values() if col in df_updated.columns]
        ].copy()

        # Преобразуем created_at в datetime и сортируем
        df_updated[orders_columns.created_at] = pd.to_datetime(df_updated[orders_columns.created_at])
        df_updated.sort_values(by=orders_columns.created_at, inplace=True)

        return df_updated

class MergeReturnsInfoStrategy(MergeStrategies):
    def __init__(self, merge_on: tuple = (returns_columns.posting_number, returns_columns.offer_id)):
        self.merge_on = merge_on

    def _add_position_counter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Добавляет временный счетчик позиций для различения дубликатов"""
        df = df.copy()
        df['_temp_position'] = df.groupby(list(self.merge_on)).cumcount()
        return df

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame):
        df1[returns_columns.posting_number] = df1[returns_columns.posting_number].astype(str)
        df1[returns_columns.offer_id] = df1[returns_columns.offer_id].astype(str)
        df2[returns_columns.posting_number] = df2[returns_columns.posting_number].astype(str)
        df2[returns_columns.offer_id] = df2[returns_columns.offer_id].astype(str)
        # Добавляем временный счетчик для обработки дубликатов
        df1_with_pos = self._add_position_counter(df1)
        df2_with_pos = self._add_position_counter(df2)

        # Полный список для индекса (включая временный счетчик)
        full_merge_on = list(self.merge_on) + ['_temp_position']

        # Устанавливаем мультииндекс
        df1_indexed = df1_with_pos.set_index(full_merge_on)
        df2_indexed = df2_with_pos.set_index(full_merge_on)

        # Объединяем с приоритетом новых данных (df2)
        df_updated = df2_indexed.combine_first(df1_indexed)

        # Сбрасываем индекс
        df_updated = df_updated.reset_index()

        # Удаляем временную колонку
        df_updated = df_updated.drop('_temp_position', axis=1)

        # Фильтруем только нужные колонки (как в оригинале)
        df_updated = df_updated[
            [col for col in asdict(returns_columns).values() if col in df_updated.columns]
        ].copy()

        # Преобразуем created_at в datetime и сортируем
        df_updated[returns_columns.return_date] = pd.to_datetime(df_updated[returns_columns.return_date])
        df_updated.sort_values(by=returns_columns.return_date, inplace=True)

        return df_updated

class MergeOrdersWithReturnsStrategy(MergeStrategies):
    def __init__(self, merge_on = [all_agg_info_columns.market, all_agg_info_columns.year, all_agg_info_columns.month, all_agg_info_columns.week, all_agg_info_columns.brand]):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged = pd.concat([df1, df2]).groupby(self.merge_on, as_index=False).sum()
        return merged