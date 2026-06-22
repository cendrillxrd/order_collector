from abc import ABC, abstractmethod
from dataclasses import asdict
from io import BytesIO
from typing import Union
import pandas as pd
import requests

from config import BASE_BRAND_NAMES
from ozon.ozon_config import BASE_COLUMNS_NAME, BASE_RETURNS_COLUMNS_NAME, BASE_RETURNS_STATUSES
from ozon.dto.orders_columns_dto import OrdersColumnsDTO
from ozon.dto.returns_columns_dto import ReturnsColumnsDTO
from ozon.utils.corr_helpers import correct_columns_name


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
        df[self.orders_columns.discount] = df[self.orders_columns.discount].str.replace('%', '', regex=False).str.strip().astype(int)
        return df


class ConvReturnsInfoStrategy(ConvertStrategy):
    def do_convert(self, data: list[dict], *args, **kwargs) -> pd.DataFrame:
        df = pd.DataFrame(data)
        product_normalized = pd.json_normalize(df['product'])
        logistic_normalized = pd.json_normalize(df['logistic'])

        # Объединяем с исходным DataFrame (если есть другие колонки)
        result = pd.concat([df.drop(['product', 'logistic'], axis=1).reset_index(drop=True) , product_normalized, logistic_normalized], axis=1)

        result = correct_columns_name(result, BASE_RETURNS_COLUMNS_NAME)

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

        for key, value in BASE_BRAND_NAMES.items():
            df[self.orders_columns.brand] = df[self.orders_columns.brand].replace(key, value)
        return df