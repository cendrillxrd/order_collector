from typing import Union

import pandas as pd

from lamoda.api_key import ApiKeyManager
from lamoda.contexts.context import ContextLamodaApi, ContextLamodaConvert
from lamoda.strategies.convert_strategies import (
    ConvOrderInfoStrategy,
    ConvOrderStrategy, ConvAllNomenclaturesStrategy)
from lamoda.strategies.request_strategies import (
    ReqOrderInfoStrategy,
    ReqOrdersStrategy, ReqFullNomenclatureStrategy)
from logger import setup_logger

logger = setup_logger("my_app")

def with_strategies(api_strategy=None, convert_strategy=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if api_strategy is not None:
                self.api_client.strategy = api_strategy()
            if convert_strategy is not None:
                self.converter.strategy = convert_strategy()
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class APIService:
    def __init__(self, api_key_manager: ApiKeyManager):
        self.api_client = ContextLamodaApi(api_key_manager=api_key_manager)
        self.converter = ContextLamodaConvert()

    @with_strategies(api_strategy=ReqFullNomenclatureStrategy, convert_strategy=ConvAllNomenclaturesStrategy)
    def get_all_nomenclatures(self, skus: list) -> Union[pd.DataFrame, list]:
        nomenclatures = self.api_client.get_info(skus=skus)
        nomenclatures_df = self.converter.convert_info(nomenclatures)
        return nomenclatures_df

    @with_strategies(api_strategy=ReqOrdersStrategy, convert_strategy=ConvOrderStrategy)
    def get_orders(self, start_date: str, end_date: str) -> Union[pd.DataFrame, list]:
        orders = self.api_client.get_info(start_date=start_date, end_date=end_date)
        orders_list = self.converter.convert_info(orders)
        return orders_list

    @with_strategies(api_strategy=ReqOrderInfoStrategy, convert_strategy=ConvOrderInfoStrategy)
    def get_orders_info(self, order_ids: list) -> pd.DataFrame:
        orders_info = []
        logger.info(f'Всего заказов {len(order_ids)}')
        i = 1
        for id in order_ids:
            logger.info(f'{i}')
            i += 1
            orders_info.append(self.api_client.get_info(order_id=id))
        orders_info_df = self.converter.convert_info(orders_info)
        return orders_info_df

    def get_orders_info_by_products(self, start_date: str, end_date: str) -> pd.DataFrame:
        orders_ids = self.get_orders(start_date, end_date)
        orders_info_df = self.get_orders_info(orders_ids)
        return orders_info_df
