from abc import ABC, abstractmethod
from dataclasses import asdict

from wb.dto.orders_columns_dto import OrdersColumnsDTO

import pandas as pd

from wb.dto.sales_columns_dto import SalesColumnsDTO
from wb.utils.corr_helpers import correct_columns_name
from wb.wb_config import BASE_COLUMNS_SALES_NAME, BASE_COLUMNS_ORDERS_NAME


class ConvertStrategy(ABC):
    def __init__(self):
        self.orders_columns = OrdersColumnsDTO()
        self.sales_columns = SalesColumnsDTO()

    @abstractmethod
    def do_convert(self, data, *args, **kwargs) -> pd.DataFrame:
        pass

class ConvOrdersStrategy(ConvertStrategy):
    def do_convert(self, data: list[dict], **kwargs) -> pd.DataFrame:
        df = pd.json_normalize(data)
        df = correct_columns_name(df, BASE_COLUMNS_ORDERS_NAME)

        df[self.orders_columns.date] = df[self.orders_columns.date].str.replace('T', ' ', regex=False)
        df[self.orders_columns.lastChangeDate] = df[self.orders_columns.lastChangeDate].str.replace('T', ' ', regex=False)

        df[self.orders_columns.brand] = df[self.orders_columns.brand].replace('PEPE JEANS LONDON', 'Pepe Jeans')
        df[self.orders_columns.brand] = df[self.orders_columns.brand].replace('MARC CONY', 'Marc Cony')
        df[self.orders_columns.price_with_discount] = df[self.orders_columns.totalPrice] * (1 - df[self.orders_columns.discountPercent] / 100)

        df = df[[col for col in asdict(self.orders_columns).values() if col in df.columns]].copy()

        return df

class ConvSalesStrategy(ConvertStrategy):
    def do_convert(self, data: list[dict], **kwargs) -> pd.DataFrame:
        df = pd.json_normalize(data)
        df = correct_columns_name(df, BASE_COLUMNS_SALES_NAME)

        df[self.sales_columns.date] = df[self.sales_columns.date].str.replace('T', ' ', regex=False)
        df[self.sales_columns.lastChangeDate] = df[self.sales_columns.lastChangeDate].str.replace('T', ' ', regex=False)

        df[self.sales_columns.brand] = df[self.sales_columns.brand].replace('PEPE JEANS LONDON', 'Pepe Jeans')
        df[self.orders_columns.brand] = df[self.orders_columns.brand].replace('MARC CONY', 'Marc Cony')
        
        df = df[[col for col in asdict(self.sales_columns).values() if col in df.columns]].copy()
        return df