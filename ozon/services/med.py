import logging

import pandas as pd

from logger import setup_logger
from ozon.strategies.convert_strategies import (ConvCollectionsMEDStrategy,)
                                           # ConvPricesMEDStrategy)
from ozon.strategies.request_strategies import (ReqCollectionsFirstMEDStrategy,
                                                ReqCollectionsSecondMEDStrategy, ReqCollectionsThirdMEDStrategy,
                                                ReqCollectionsFourthMEDStrategy, )
                                           # ReqPricesMEDStrategy)
from ozon.workers.client import MedClient
from ozon.workers.converter import Converter
logger = setup_logger("my_app")

def with_strategies(med_strategy_cls, converter_strategy_cls):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            self.med.set_strategy(med_strategy_cls())
            self.converter.set_strategy(converter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class MEDService:
    def __init__(self):
        self.med = MedClient()
        self.converter = Converter()

    @with_strategies(ReqCollectionsFirstMEDStrategy, ConvCollectionsMEDStrategy)
    def get_med_collections_first(self) -> pd.DataFrame:
        logger.info(f'Получение коллекций по первой ссылке')
        med_collections_csv = self.med.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df

    @with_strategies(ReqCollectionsSecondMEDStrategy, ConvCollectionsMEDStrategy)
    def get_med_collections_second(self) -> pd.DataFrame:
        logger.info(f'Получение коллекций по второй ссылке')
        med_collections_csv = self.med.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df

    @with_strategies(ReqCollectionsThirdMEDStrategy, ConvCollectionsMEDStrategy)
    def get_med_collections_third(self) -> pd.DataFrame:
        logger.info(f'Получение коллекций по третьей ссылке')
        med_collections_csv = self.med.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df

    @with_strategies(ReqCollectionsFourthMEDStrategy, ConvCollectionsMEDStrategy)
    def get_med_collections_fourth(self) -> pd.DataFrame:
        logger.info(f'Получение коллекций по четвертой ссылке')
        med_collections_csv = self.med.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df
