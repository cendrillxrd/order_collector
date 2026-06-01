from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Union

from wb.dto.orders_columns_dto import OrdersColumnsDTO

import pandas as pd

from wb.dto.sales_columns_dto import SalesColumnsDTO
from wb.utils.corr_helpers import correct_columns_name


class ConverterStrategy(ABC):
    def __init__(self):
        pass
        self.orders_columns = OrdersColumnsDTO()
        self.sales_columns = SalesColumnsDTO()

    @abstractmethod
    def converting(self, data, **kwargs) -> Union[pd.DataFrame, str]:
        pass

class ConvOrdersStrategy(ConverterStrategy):
    def converting(self, data: list[dict], **kwargs) -> pd.DataFrame:
        df = pd.json_normalize(data)
        df = correct_columns_name(df, 'orders')
        df[self.orders_columns.date] = df[self.orders_columns.date].str.replace('T', ' ', regex=False)
        df[self.orders_columns.lastChangeDate] = df[self.orders_columns.lastChangeDate].str.replace('T', ' ', regex=False)
        df = df[
            [col for col in asdict(self.orders_columns).values() if col in df.columns]].copy()

        return df

class ConvSalesStrategy(ConverterStrategy):
    def converting(self, data: list[dict], **kwargs) -> pd.DataFrame:
        df = pd.json_normalize(data)
        df = correct_columns_name(df, 'sales')
        df[self.sales_columns.date] = df[self.sales_columns.date].str.replace('T', ' ', regex=False)
        df[self.sales_columns.lastChangeDate] = df[self.sales_columns.lastChangeDate].str.replace('T', ' ', regex=False)
        return df