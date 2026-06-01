import time
from typing import Literal, Union

import pandas as pd

from logger import setup_logger
from ozon.config import TIME_SLEEP_CARDS_LINK
from ozon.dto.orders_columns_dto import OrdersColumnsDTO
from ozon.strategies.convert_strategies import ConvOrdersInfoStrategy, ConvReturnsInfoStrategy, ConvCardsInfoStrategy
from ozon.strategies.request_strategies import ReqOrdersInfoReportStrategy, ReqGetLinkStrategy, ReqGetLinkDataStrategy, \
    ReqReturnsInfoReportStrategy, ReqCardsInfoReportStrategy
from ozon.workers.client import OzonAPIClient, HttpClient
from ozon.workers.converter import Converter

logger = setup_logger("my_app")

def with_strategies(type: Literal['api', 'http', 'ozon_http']=None, ozon_strategy_cls=None, converter_strategy_cls=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if ozon_strategy_cls is not None:
                if type == 'api':
                    self.ozon_api_client.set_strategy(ozon_strategy_cls())
                elif type == 'http':
                    self.http_client.set_strategy(ozon_strategy_cls())
                else:
                    self.ozon_http_client.set_strategy(ozon_strategy_cls())
            if converter_strategy_cls is not None:
                self.converter.set_strategy(converter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator

class OzonService:
    def __init__(self):
        self.ozon_api_client = OzonAPIClient()
        self.converter = Converter()
        self.http_client = HttpClient()
        self.orders_columns = OrdersColumnsDTO()

    @with_strategies(converter_strategy_cls=ConvOrdersInfoStrategy)
    def get_orders(self) -> Union[pd.DataFrame, None]:
        logger.info(f'Получение информации о заказах (OZON)')
        orders_fbs_code = self.create_info_report_orders(schema='fbs')
        orders_fbo_code = self.create_info_report_orders(schema='fbo')
        result = []
        for code in (orders_fbs_code, orders_fbo_code):
            time.sleep(TIME_SLEEP_CARDS_LINK)
            file_link = self.get_info_link(code)
            if file_link:
                orders = self.get_info_report(file_link)
                orders_df = self.converter.convert(orders)
                result.append(orders_df)
            else:
                return None
        combined = pd.concat(result)
        combined[self.orders_columns.created_at] = pd.to_datetime(combined[self.orders_columns.created_at])
        combined.sort_values(by=self.orders_columns.created_at, inplace=True)
        return combined

    @with_strategies(converter_strategy_cls=ConvReturnsInfoStrategy)
    def get_returns(self):
        logger.info(f'Получение информации о возвратах (OZON)')
        returns= self.get_info_about_returns()
        returns_df = self.converter.convert(returns)
        return returns_df

    @with_strategies('api', ReqOrdersInfoReportStrategy)
    def create_info_report_orders(self, schema: Literal['fbs', 'fbo']) -> str:
        logger.info(f'Создание отчета по заказам (OZON)')
        code = self.ozon_api_client.get_data(schema=schema)
        return code

    @with_strategies('api', ReqGetLinkStrategy)
    def get_info_link(self, code: str) -> str:
        logger.info(f'Получение ссылки на отчет (OZON)')
        file_link = self.ozon_api_client.get_data(code=code)
        return file_link

    @with_strategies('http', ReqGetLinkDataStrategy)
    def get_info_report(self, link: str) -> list[dict]:
        logger.info(f'Получение отчета (OZON)')
        orders_info = self.http_client.get_data(link=link)
        return orders_info

    @with_strategies('api', ReqReturnsInfoReportStrategy)
    def get_info_about_returns(self) -> list[dict]:
        returns_info = self.ozon_api_client.get_data()
        return returns_info

    @with_strategies(converter_strategy_cls=ConvCardsInfoStrategy)
    def get_cards_info(self) -> pd.DataFrame:
        visibilities = ['ALL', 'ARCHIVED']
        result = []
        for visibility in visibilities:
            code = self.create_info_report_cards(visibility=visibility)
            time.sleep(TIME_SLEEP_CARDS_LINK)
            file_link = self.get_info_link(code)
            if file_link:
                cards = self.get_info_report(file_link)
                cards_df = self.converter.convert(cards)
                result.append(cards_df)
            else:
                cards_df = None
                result.append(cards_df)
        combined = pd.concat(result)
        return combined

    @with_strategies('api', ReqCardsInfoReportStrategy)
    def create_info_report_cards(self, visibility: str) -> str:
        code = self.ozon_api_client.get_data(visibility=visibility)
        return code