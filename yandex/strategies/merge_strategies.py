from abc import ABC, abstractmethod
from dataclasses import asdict

import pandas as pd

from yandex.dto.all_agg_info_dto import AllAggInfoColumnsDTO
from yandex.dto.orders_columns import OrdersColumnsDTO
from yandex.dto.returned_columns_dto import ReturnedColumnsDTO

orders_columns = OrdersColumnsDTO()
returns_columns = ReturnedColumnsDTO()
all_agg_info_columns = AllAggInfoColumnsDTO()

class MergeStrategy(ABC):
    @abstractmethod
    def do_merge(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        pass

class MergeCollections(MergeStrategy):
    def do_merge(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        merged_df = pd.concat([df1, df2], ignore_index=True)
        return merged_df

class MergeYandexCollections(MergeStrategy):
    def __init__(self, merge_on: str = orders_columns.offer_id):
        self.merge_on = merge_on

    def do_merge(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        df1[self.merge_on] = df1[self.merge_on].astype(str)
        df2[self.merge_on] = df2[self.merge_on].astype(str)
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergeOrdersInfoStrategy(MergeStrategy):
    def __init__(self, merge_on: tuple = (orders_columns.order_id, orders_columns.offer_id)):
        self.merge_on = merge_on

    def _add_position_counter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Добавляет временный счетчик позиций для различения дубликатов"""
        df = df.copy()
        df['_temp_position'] = df.groupby(list(self.merge_on)).cumcount()
        return df

    def do_merge(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs):
        df1[orders_columns.order_id] = df1[orders_columns.order_id].astype(str)
        df1[orders_columns.offer_id] = df1[orders_columns.offer_id].astype(str)
        df2[orders_columns.order_id] = df2[orders_columns.order_id].astype(str)
        df2[orders_columns.offer_id] = df2[orders_columns.offer_id].astype(str)
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
        df_updated[orders_columns.creation_date] = pd.to_datetime(df_updated[orders_columns.creation_date])
        df_updated.sort_values(by=orders_columns.creation_date, inplace=True)

        return df_updated

class MergeReturnsInfoStrategy(MergeStrategy):
    def __init__(self, merge_on: tuple = (returns_columns.order_id, returns_columns.offer_id)):
        self.merge_on = merge_on

    def _add_position_counter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Добавляет временный счетчик позиций для различения дубликатов"""
        df = df.copy()
        df['_temp_position'] = df.groupby(list(self.merge_on)).cumcount()
        return df

    def do_merge(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs):
        df1[returns_columns.order_id] = df1[returns_columns.order_id].astype(str)
        df1[returns_columns.offer_id] = df1[returns_columns.offer_id].astype(str)
        df2[returns_columns.order_id] = df2[returns_columns.order_id].astype(str)
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
        df_updated[returns_columns.creation_date] = pd.to_datetime(df_updated[returns_columns.creation_date])
        df_updated.sort_values(by=returns_columns.creation_date, inplace=True)

        return df_updated

class MergeOrdersWithReturnsStrategy(MergeStrategy):
    def __init__(self):
        self.merge_on = [all_agg_info_columns.market,
                         all_agg_info_columns.year,
                         all_agg_info_columns.month,
                         all_agg_info_columns.week,
                         all_agg_info_columns.brand]

    def do_merge(self, df1: pd.DataFrame, df2: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        merged = pd.concat([df1, df2]).groupby(self.merge_on, as_index=False).sum()
        return merged