from abc import ABC, abstractmethod
from dataclasses import asdict
from io import BytesIO

import pandas as pd

from yandex.config import BASE_ORDERS_COLUMNS_NAME, BASE_COLLECTIONS_COLUMNS_NAME, BASE_RETURNS_COLUMNS_NAME
from yandex.dto.orders_columns import OrdersColumnsDTO
from yandex.dto.returned_columns_dto import ReturnedColumnsDTO
from yandex.utils.corr_helpers import correct_columns_name


class ConvertStrategy(ABC):
    def __init__(self):
        self.orders_columns = OrdersColumnsDTO()
        self.returned_columns = ReturnedColumnsDTO()

    @abstractmethod
    def do_convert(self, data, **kwargs) -> pd.DataFrame:
        pass

class ConvYandexOrders(ConvertStrategy):
    def do_convert(self, data: dict, **kwargs) -> pd.DataFrame:
        df = pd.DataFrame(data)
        # 2. Разворачиваем (explode) столбец items — каждый элемент списка становится отдельной строкой
        df_exploded = df.explode('items', ignore_index=True)

        # 3. Нормализуем словарь из колонки items в отдельные колонки
        # При этом сохраняем все остальные поля заказа
        items_normalized = pd.json_normalize(df_exploded['items'])
        # Удаляем старую колонку items (она теперь в разобранном виде)
        df_exploded = df_exploded.drop(columns=['items'])

        # 4. Объединяем с нормализованными данными о товарах
        result_df = pd.concat([df_exploded, items_normalized], axis=1)

        prices_normalized = pd.json_normalize(result_df['prices'])
        # Переименуем колонки, чтобы не путать с общими ценами заказа
        prices_normalized = prices_normalized.add_prefix('item_prices.')
        result_df = pd.concat([result_df.drop(columns=['prices']), prices_normalized], axis=1)

        # 6. (Опционально) переименуйте колонки для наглядности
        # Например, чтобы не путать item.id с orderId
        result_df = result_df.rename(columns={'id': 'item_id', 'offerId': 'offer_id', 'offerName': 'offer_name'})

        result_df = correct_columns_name(result_df, BASE_ORDERS_COLUMNS_NAME)

        result_df_without_unnecessary_columns = result_df[[col for col in asdict(self.orders_columns).values() if col in result_df.columns]].copy()

        date_columns = [
            self.orders_columns.creation_date,
            self.orders_columns.update_date
        ]

        for col in date_columns:
            if col in result_df_without_unnecessary_columns.columns:
                result_df_without_unnecessary_columns[col] = pd.to_datetime(
                    result_df_without_unnecessary_columns[col],
                    format='ISO8601',  # Автоматически определяет оба формата
                    errors='coerce'
                )
                # Убираем timezone
                result_df_without_unnecessary_columns[col] = result_df_without_unnecessary_columns[col].dt.tz_localize(
                    None)


        return result_df_without_unnecessary_columns

class ConvYandexReturns(ConvertStrategy):
    def do_convert(self, data: dict, **kwargs) -> pd.DataFrame:
        df = pd.DataFrame(data)

        # 2. Разворачиваем (explode) столбец items — каждый элемент списка становится отдельной строкой
        df_exploded = df.explode('items', ignore_index=True)

        # 3. Нормализуем словарь из колонки items в отдельные колонки
        # При этом сохраняем все остальные поля заказа
        items_normalized = pd.json_normalize(df_exploded['items'])
        # Удаляем старую колонку items (она теперь в разобранном виде)
        df_exploded = df_exploded.drop(columns=['items'])

        # 4. Объединяем с нормализованными данными о товарах
        result_df = pd.concat([df_exploded, items_normalized], axis=1)

        df_exploded = result_df.explode('decisions', ignore_index=True)
        items_normalized = pd.json_normalize(df_exploded['decisions'])
        # Удаляем старую колонку decisions (она теперь в разобранном виде)
        df_exploded = df_exploded.drop(columns=['decisions'])

        # 4. Объединяем с нормализованными данными о товарах
        result_df = pd.concat([df_exploded, items_normalized], axis=1)

        columns_name = [column for column in result_df.columns if column in BASE_RETURNS_COLUMNS_NAME]

        columns_rename = {k: BASE_RETURNS_COLUMNS_NAME.get(k) for k in columns_name}
        result_df.rename(columns_rename,
                         inplace=True,
                         axis=1)

        result_df_without_unnecessary_columns = result_df[
            [col for col in asdict(self.returned_columns).values() if col in result_df.columns]].copy()

        date_columns = [
            self.returned_columns.creation_date,
            self.returned_columns.update_date
        ]

        for col in date_columns:
            if col in result_df_without_unnecessary_columns.columns:
                result_df_without_unnecessary_columns[col] = pd.to_datetime(
                    result_df_without_unnecessary_columns[col],
                    format='ISO8601',  # Автоматически определяет оба формата
                    errors='coerce'
                )
                # Убираем timezone
                result_df_without_unnecessary_columns[col] = result_df_without_unnecessary_columns[col].dt.tz_localize(
                    None)
        cols = result_df_without_unnecessary_columns.columns.tolist()
        dup_positions = [i for i, name in enumerate(cols) if name == self.returned_columns.count]

        # Удалить, скажем, вторую (индекс 1 в списке dup_positions)
        result_df_without_unnecessary_columns = result_df_without_unnecessary_columns.iloc[:, [i for i in range(len(cols)) if i != dup_positions[1]]]
        return result_df_without_unnecessary_columns

class ConvMEDCollections(ConvertStrategy):
    def do_convert(self, data, **kwargs) -> pd.DataFrame:
        """Преобразует данные о коллекциях на меде в DataFrame"""
        med_collections_df = pd.read_excel(BytesIO(data.content))

        med_collections_df = correct_columns_name(med_collections_df, BASE_COLLECTIONS_COLUMNS_NAME)

        med_collections_df_without_unnecessary_columns = med_collections_df[[self.orders_columns.offer_id,
                                                                             self.orders_columns.brand,]]
        return med_collections_df_without_unnecessary_columns