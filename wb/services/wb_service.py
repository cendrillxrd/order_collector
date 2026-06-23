from typing import Literal, Union

import pandas as pd

from logger import setup_logger
from wb.contexts.context import ContextWbApi
from wb.contexts.context import ContextWbConvert
from wb.strategies.convert_strategies import (ConvOrdersStrategy, ConvSalesStrategy,
                                                      )
from wb.strategies.request_strategies import (ReqOrdersStrategy, ReqSalesStrategy,
                                                      )
logger = setup_logger("my_app")

def with_strategies(api_strategy=None, convert_strategy=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if api_strategy is not None:
                self.wb_api_client.strategy = api_strategy()
            if convert_strategy is not None:
                self.converter.strategy = convert_strategy()
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class WBService:
    def __init__(self):
        self.wb_api_client = ContextWbApi()
        self.converter = ContextWbConvert()

    @with_strategies(api_strategy=ReqOrdersStrategy, convert_strategy=ConvOrdersStrategy)
    def get_orders(self, date_from: str, date_to: str) -> pd.DataFrame:
        logger.info(f'Получение информации о заказах (WB)')
        orders = self.wb_api_client.get_info(date_from=date_from, date_to=date_to)
        orders_df = self.converter.convert_info(orders)
        return orders_df

    @with_strategies(api_strategy=ReqSalesStrategy, convert_strategy=ConvSalesStrategy)
    def get_sales(self, date_from: str, date_to: str) -> pd.DataFrame:
        logger.info(f'Получение информации о продажах/возвратах (WB)')
        sales = self.wb_api_client.get_info(date_from=date_from, date_to=date_to)
        sales_df = self.converter.convert_info(sales)
        return sales_df