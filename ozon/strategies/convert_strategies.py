from abc import ABC, abstractmethod
from dataclasses import asdict
from io import BytesIO
from typing import Union
import pandas as pd

from ozon.config import BASE_COLUMNS_NAME, BASE_RETURNS_COLUMNS_NAME, BASE_RETURNS_STATUSES
from ozon.dto.orders_columns_dto import OrdersColumnsDTO
from ozon.dto.returns_columns_dto import ReturnsColumnsDTO


class ConverterStrategy(ABC):
    def __init__(self):
        self.orders_columns = OrdersColumnsDTO()
        self.returns_columns = ReturnsColumnsDTO()

    @abstractmethod
    def converting(self, data) -> Union[pd.DataFrame, list]:
        pass

class ConvOrdersInfoStrategy(ConverterStrategy):
    def converting(self, data) -> pd.DataFrame:
        df = pd.read_csv(BytesIO(data.content), encoding='utf-8', sep=';')
        df = df[[col for col in asdict(self.orders_columns).values() if col in df.columns]].copy()
        return df


class ConvReturnsInfoStrategy(ConverterStrategy):
    def converting(self, data) -> pd.DataFrame:
        df = pd.DataFrame(data)
        product_normalized = pd.json_normalize(df['product'])
        logistic_normalized = pd.json_normalize(df['logistic'])

        # Объединяем с исходным DataFrame (если есть другие колонки)
        result = pd.concat([df.drop(['product', 'logistic'], axis=1).reset_index(drop=True) , product_normalized, logistic_normalized], axis=1)

        columns_name = [column for column in result.columns if column in BASE_RETURNS_COLUMNS_NAME]

        columns_rename = {k: BASE_RETURNS_COLUMNS_NAME.get(k) for k in columns_name}
        result.rename(columns_rename,
                                  inplace=True,
                                  axis=1)
        result = result[[col for col in asdict(self.returns_columns).values() if col in result.columns]].copy()
        result = result[result[self.returns_columns.type].isin(BASE_RETURNS_STATUSES)].copy()

        result[self.returns_columns.return_date] = pd.to_datetime(
            result[self.returns_columns.return_date],
            format='ISO8601'
        )

        # Теперь преобразуем в нужный строковый формат
        result[self.returns_columns.return_date] = result[self.returns_columns.return_date].dt.strftime("%Y-%m-%d %H:%M:%S")
        return result

class ConvCollectionsMEDStrategy(ConverterStrategy):
    def converting(self, data, **kwargs) -> pd.DataFrame:
        """Преобразует данные о ценах на меде в DataFrame"""
        med_collections_df = pd.read_excel(BytesIO(data.content))
        med_collections_df.drop('Артикул', axis=1, inplace=True)
        columns_name = [column for column in med_collections_df.columns if column in BASE_COLUMNS_NAME]

        columns_rename = {k: BASE_COLUMNS_NAME.get(k) for k in columns_name}
        med_collections_df.rename(columns_rename,
                                  inplace=True,
                                  axis=1)
        med_collections_df = med_collections_df[[self.orders_columns.offer_id, self.orders_columns.brand]]

        return med_collections_df

class ConvCardsInfoStrategy(ConverterStrategy):
    def converting(self, data) -> pd.DataFrame:
        df = pd.read_csv(BytesIO(data.content), encoding='utf-8', sep=';')
        df = df[[self.orders_columns.sku, self.orders_columns.brand]]
        return df