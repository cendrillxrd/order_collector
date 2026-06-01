from typing import Literal

import pandas as pd

from lamoda.strategies.convert_strategies import (
    ConvMEDCollections,
    ConvOrderInfoStrategy,
    ConvOrderStrategy, ConvAllNomenclaturesStrategy)
from lamoda.strategies.request_strategies import (
    ReqMEDCollectionsFirst,
    ReqMEDCollectionsFourth,
    ReqMEDCollectionsSecond,
    ReqMEDCollectionsThird,
    ReqOrderInfoStrategy,
    ReqOrdersStrategy, ReqFullNomenclatureStrategy)
from lamoda.workers.api_client import APIClient, MedClient
from lamoda.workers.converter import Converter
from logger import setup_logger

logger = setup_logger("my_app")

def with_strategies(wb_strategy_cls, converter_strategy_cls):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            self.api_client.set_strategy(wb_strategy_cls())
            self.converter.set_strategy(converter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class APIService:
    def __init__(self, api_key_manager: 'ApiKeyManager'):
        self.api_client = APIClient(api_key_manager=api_key_manager)
        self.converter = Converter()

    @with_strategies(ReqFullNomenclatureStrategy, ConvAllNomenclaturesStrategy)
    def get_all_nomenclatures(self, skus: list) -> pd.DataFrame:
        nomenclatures = self.api_client.get_data(skus=skus)
        nomenclatures_df = self.converter.convert(nomenclatures)
        return nomenclatures_df

    @with_strategies(ReqOrdersStrategy, ConvOrderStrategy)
    def get_orders(self, start_date: str = None, end_date: str = None) -> list:
        orders = self.api_client.get_data(start_date=start_date, end_date=end_date)
        orders_list = self.converter.convert(orders)
        return orders_list

    @with_strategies(ReqOrderInfoStrategy, ConvOrderInfoStrategy)
    def get_orders_info(self, order_ids: list) -> pd.DataFrame:
        orders_info = []
        logger.info(f'Всего заказов {len(order_ids)}')
        i = 1
        for id in order_ids:
            logger.info(f'{i}')
            i += 1
            orders_info.append(self.api_client.get_data(order_id=id))
        orders_info_df = self.converter.convert(orders_info)
        return orders_info_df

    def get_orders_info_by_products(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        orders_id = self.get_orders(start_date=start_date, end_date=end_date)
        orders_info_df = self.get_orders_info(orders_id)
        return orders_info_df


def with_strategies_med(req_strategy_cls=None, converter_strategy_cls=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if req_strategy_cls is not None:
                self.med_api_client.set_strategy(req_strategy_cls())
            if converter_strategy_cls is not None:
                self.converter.set_strategy(converter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class MedService:
    def __init__(self):
        self.med_api_client = MedClient()
        self.converter = Converter()

    @with_strategies_med(req_strategy_cls=ReqMEDCollectionsFirst, converter_strategy_cls=ConvMEDCollections)
    def get_med_collections_first(self) -> pd.DataFrame:
        med_collections_csv = self.med_api_client.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df

    @with_strategies_med(req_strategy_cls=ReqMEDCollectionsSecond, converter_strategy_cls=ConvMEDCollections)
    def get_med_collections_second(self) -> pd.DataFrame:
        med_collections_csv = self.med_api_client.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df

    @with_strategies_med(req_strategy_cls=ReqMEDCollectionsThird, converter_strategy_cls=ConvMEDCollections)
    def get_med_collections_third(self) -> pd.DataFrame:
        med_collections_csv = self.med_api_client.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df

    @with_strategies_med(req_strategy_cls=ReqMEDCollectionsFourth, converter_strategy_cls=ConvMEDCollections)
    def get_med_collections_fourth(self) -> pd.DataFrame:
        med_collections_csv = self.med_api_client.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df
