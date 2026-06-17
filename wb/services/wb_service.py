from typing import Literal, Union

import pandas as pd

from logger import setup_logger
from wb.context.context_wb_api import ContextWbApi
from wb.context.convext_wb_convert import ContextWbConvert
from wb.strategies.convert_strategies import (ConvOrdersStrategy, ConvSalesStrategy,
                                                      )
from wb.strategies.request_strategies import (ReqOrdersStrategy, ReqSalesStrategy,
                                                      )
logger = setup_logger("my_app")

def with_strategies(client_type: Literal['api', 'http'], api_strategy=None, converter_strategy=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if api_strategy is not None:
                if client_type == 'api':
                    self.wb_api_client.strategy = api_strategy()
                else:
                    self.wb_http_client.strategy = api_strategy()
            if converter_strategy is not None:
                self.converter.strategy = converter_strategy()
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class WBService:
    def __init__(self):
        self.wb_api_client = ContextWbApi()
        self.converter = ContextWbConvert()

    @with_strategies(client_type='api', api_strategy=ReqOrdersStrategy, converter_strategy=ConvOrdersStrategy)
    def get_orders(self, date_from: str, date_to: str) -> pd.DataFrame:
        logger.info(f'Получение информации о заказах (WB)')
        orders = self.wb_api_client.get_info(date_from=date_from, date_to=date_to)
        orders_df = self.converter.convert_info(orders)
        return orders_df

    @with_strategies(client_type='api', api_strategy=ReqSalesStrategy, converter_strategy=ConvSalesStrategy)
    def get_sales(self, date_from: str, date_to: str) -> pd.DataFrame:
        logger.info(f'Получение информации о продажах/возвратах (WB)')
        sales = self.wb_api_client.get_info(date_from=date_from, date_to=date_to)
        sales_df = self.converter.convert_info(sales)
        return sales_df