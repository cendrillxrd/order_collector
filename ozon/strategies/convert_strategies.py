from abc import ABC, abstractmethod
from dataclasses import asdict
from io import BytesIO
from typing import Union
import pandas as pd
import requests

from ozon.ozon_config import BASE_COLUMNS_NAME, BASE_RETURNS_COLUMNS_NAME, BASE_RETURNS_STATUSES
from ozon.dto.orders_columns_dto import OrdersColumnsDTO
from ozon.dto.returns_columns_dto import ReturnsColumnsDTO


class ConvertStrategy(ABC):
    def __init__(self):
        self.orders_columns = OrdersColumnsDTO()
        self.returns_columns = ReturnsColumnsDTO()

    @abstractmethod
    def do_convert(self, data: list[dict] | requests.Response, *args, **kwargs) -> pd.DataFrame:
        pass

class ConvOrdersInfoStrategy(ConvertStrategy):
    def do_convert(self, data: requests.Response, *args, **kwargs) -> pd.DataFrame:
        df = pd.read_csv(BytesIO(data.content), encoding='utf-8', sep=';')
        df = df[[col for col in asdict(self.orders_columns).values() if col in df.columns]].copy()
        return df


class ConvReturnsInfoStrategy(ConvertStrategy):
    def do_convert(self, data: list[dict], *args, **kwargs) -> pd.DataFrame:
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


class ConvCardsInfoStrategy(ConvertStrategy):
    def do_convert(self, data: requests.Response, *args, **kwargs) -> pd.DataFrame:
        df = pd.read_csv(BytesIO(data.content), encoding='utf-8', sep=';')
        df = df[[self.orders_columns.sku, self.orders_columns.brand]]
        return df