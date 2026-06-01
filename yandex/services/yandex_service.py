import time
from typing import Literal, Union

import pandas as pd

from logger import setup_logger
from yandex.config import TIME_SLEEP_REPORT
from yandex.strategies.requests_strategies import ReqYandexOrders, ReqYandexBusinessId, ReqYandexCampaignId, \
    ReqYandexReturns
from yandex.strategies.convert_strategies import ConvYandexOrders, ConvYandexReturns
from yandex.workers.client import YandexAPIClient
from yandex.workers.converter import Converter
logger = setup_logger("my_app")


def with_strategies(req_strategy_cls = None, converter_strategy_cls = None, type: str = Literal['api, http']):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if req_strategy_cls is not None:
                if type == 'api':
                    self.yandex_api_client.set_strategy(req_strategy_cls())
                else:
                    self.http_client.set_strategy(req_strategy_cls())
            if converter_strategy_cls is not None:
                self.converter.set_strategy(converter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator

class YandexService:
    def __init__(self):
        self.yandex_api_client = YandexAPIClient()
        self.converter = Converter()

    @with_strategies(req_strategy_cls=ReqYandexBusinessId, type='api')
    def get_business_id(self) -> int:
        business_id = self.yandex_api_client.get_data()
        return business_id

    @with_strategies(req_strategy_cls=ReqYandexCampaignId, type='api')
    def get_campaign_id(self) -> int:
        campaign_id = self.yandex_api_client.get_data()
        return campaign_id

    @with_strategies(req_strategy_cls=ReqYandexOrders, converter_strategy_cls=ConvYandexOrders, type='api')
    def get_orders_by_business_id(self, business_id: int) -> pd.DataFrame:
        orders = self.yandex_api_client.get_data(business_id=business_id)
        orders_df = self.converter.convert(orders)
        return orders_df

    @with_strategies(req_strategy_cls=ReqYandexReturns, converter_strategy_cls=ConvYandexReturns, type='api')
    def get_returns_by_campaign_id(self, campaign_id: int, date_from: str, date_to: str) -> pd.DataFrame:
        returns = self.yandex_api_client.get_data(campaign_id=campaign_id, date_to=date_to, date_from=date_from)
        returns_df = self.converter.convert(returns)
        return returns_df

    def get_orders(self) -> pd.DataFrame:
        business_id = self.get_business_id()
        orders = self.get_orders_by_business_id(business_id)
        return orders

    def get_returns(self, date_from: str, date_to: str) -> pd.DataFrame:
        campaign_id = self.get_campaign_id()
        returns = self.get_returns_by_campaign_id(campaign_id, date_from, date_to)
        return returns


