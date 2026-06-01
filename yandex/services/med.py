import pandas as pd

from yandex.strategies.requests_strategies import (ReqMEDCollectionsFirst, ReqMEDCollectionsSecond, ReqMEDCollectionsThird,
                        ReqMEDCollectionsFourth)
from yandex.strategies.convert_strategies import ConvMEDCollections
from yandex.workers.converter import Converter
from yandex.workers.client import MedClient


def with_strategies(req_strategy_cls = None, converter_strategy_cls = None):
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

    @with_strategies(req_strategy_cls=ReqMEDCollectionsFirst, converter_strategy_cls=ConvMEDCollections)
    def get_med_collections_first(self) -> pd.DataFrame:
        med_collections_csv = self.med_api_client.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df

    @with_strategies(req_strategy_cls=ReqMEDCollectionsSecond, converter_strategy_cls=ConvMEDCollections)
    def get_med_collections_second(self) -> pd.DataFrame:
        med_collections_csv = self.med_api_client.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df

    @with_strategies(req_strategy_cls=ReqMEDCollectionsThird, converter_strategy_cls=ConvMEDCollections)
    def get_med_collections_third(self) -> pd.DataFrame:
        med_collections_csv = self.med_api_client.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df

    @with_strategies(req_strategy_cls=ReqMEDCollectionsFourth, converter_strategy_cls=ConvMEDCollections)
    def get_med_collections_fourth(self) -> pd.DataFrame:
        med_collections_csv = self.med_api_client.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df