from typing import Literal

import pandas as pd

from logger import setup_logger
from wb.strategies.convert_strategies import (ConvOrdersStrategy, ConvSalesStrategy,
                                                      )
from wb.strategies.request_strategies import (ReqOrdersStrategy, ReqSalesStrategy,
                                                      )

from wb.workers.client import WildberriesAPIClient
from wb.workers.converter import Converter

logger = setup_logger("my_app")

def with_strategies(type: Literal['api', 'http'], wb_strategy_cls=None, converter_strategy_cls=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if wb_strategy_cls is not None:
                if type == 'api':
                    self.wb_api_client.set_strategy(wb_strategy_cls())
                else:
                    self.wb_http_client.set_strategy(wb_strategy_cls())
            if converter_strategy_cls is not None:
                self.converter.set_strategy(converter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class WBService:
    def __init__(self):
        self.wb_api_client = WildberriesAPIClient()
        self.converter = Converter()

    @with_strategies('api', ReqOrdersStrategy, ConvOrdersStrategy)
    def get_orders(self, date_from: str, date_to: str) -> pd.DataFrame:
        logger.info(f'Получение информации о заказах (WB)')
        orders = self.wb_api_client.get_data(date_from=date_from, date_to=date_to)
        orders_df = self.converter.convert(orders)
        return orders_df

    @with_strategies('api', ReqSalesStrategy, ConvSalesStrategy)
    def get_sales(self, date_from: str, date_to: str) -> pd.DataFrame:
        logger.info(f'Получение информации о продажах/возвратах (WB)')
        sales = self.wb_api_client.get_data(date_from=date_from, date_to=date_to)
        sales_df = self.converter.convert(sales)
        return sales_df