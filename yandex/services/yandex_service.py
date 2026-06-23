import pandas as pd

from logger import setup_logger
from yandex.contexts.context import ContextYandexApi, ContextYandexConvert
from yandex.strategies.requests_strategies import ReqYandexOrders, ReqYandexBusinessId, ReqYandexCampaignId, \
    ReqYandexReturns
from yandex.strategies.convert_strategies import ConvYandexOrders, ConvYandexReturns

logger = setup_logger("my_app")


def with_strategies(api_strategy = None, convert_strategy = None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if api_strategy is not None:
                self.yandex_api_client.strategy = api_strategy()
            if convert_strategy is not None:
                self.converter.strategy = convert_strategy()
            return method(self, *args, **kwargs)

        return wrapper

    return decorator

class YandexService:
    def __init__(self):
        self.yandex_api_client = ContextYandexApi()
        self.converter = ContextYandexConvert()

    @with_strategies(api_strategy=ReqYandexBusinessId)
    def get_business_id(self) -> int:
        business_id = self.yandex_api_client.get_info()
        return business_id

    @with_strategies(api_strategy=ReqYandexCampaignId)
    def get_campaign_id(self) -> int:
        campaign_id = self.yandex_api_client.get_info()
        return campaign_id

    @with_strategies(api_strategy=ReqYandexOrders, convert_strategy=ConvYandexOrders)
    def get_orders_by_business_id(self, business_id: int) -> pd.DataFrame:
        orders = self.yandex_api_client.get_info(business_id=business_id)
        orders_df = self.converter.convert_info(orders)
        return orders_df

    @with_strategies(api_strategy=ReqYandexReturns, convert_strategy=ConvYandexReturns)
    def get_returns_by_campaign_id(self, campaign_id: int, date_from: str, date_to: str) -> pd.DataFrame:
        returns = self.yandex_api_client.get_info(campaign_id=campaign_id, date_to=date_to, date_from=date_from)
        returns_df = self.converter.convert_info(returns)
        return returns_df

    def get_orders(self) -> pd.DataFrame:
        logger.info(f'Получение информации о заказах (YANDEX)')
        business_id = self.get_business_id()
        orders = self.get_orders_by_business_id(business_id)
        return orders

    def get_returns(self, date_from: str, date_to: str) -> pd.DataFrame:
        logger.info(f'Получение информации о возвраты (YANDEX)')
        campaign_id = self.get_campaign_id()
        returns = self.get_returns_by_campaign_id(campaign_id, date_from, date_to)
        return returns


