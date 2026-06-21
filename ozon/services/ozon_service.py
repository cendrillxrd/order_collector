import time
from typing import Literal

import pandas as pd

from logger import setup_logger
from ozon.contexts.context import ContextConvert
from ozon.contexts.context import ContextHTTP
from ozon.contexts.context import ContextOZONApi
from ozon.ozon_config import TIME_SLEEP_CARDS_LINK, SCHEMAS, VISIBILITIES
from ozon.dto.orders_columns_dto import OrdersColumnsDTO
from ozon.strategies.convert_strategies import ConvOrdersInfoStrategy, ConvReturnsInfoStrategy, ConvCardsInfoStrategy
from ozon.strategies.request_strategies import ReqOrdersInfoReportStrategy, ReqGetLinkStrategy, ReqGetLinkDataStrategy, \
    ReqReturnsInfoReportStrategy, ReqCardsInfoReportStrategy

logger = setup_logger("my_app")


def with_strategies(client_type: Literal['api', 'http'] | None = None, request_strategy=None, convert_strategy=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if request_strategy is not None:
                if client_type == 'api':
                    self.ozon_api_client.strategy = request_strategy()
                elif client_type == 'http':
                    self.http_client.strategy = request_strategy()
            if convert_strategy is not None:
                self.converter.strategy = convert_strategy()
            return method(self, *args, **kwargs)

        return wrapper

    return decorator

class OzonService:
    def __init__(self):
        self.ozon_api_client = ContextOZONApi()
        self.converter = ContextConvert()
        self.http_client = ContextHTTP()
        self.orders_columns = OrdersColumnsDTO()

    @with_strategies(convert_strategy=ConvOrdersInfoStrategy)
    def get_orders(self, processed_at_from: str, processed_at_to: str) -> pd.DataFrame:
        codes = {
            schema: self.create_info_report_orders(schema, processed_at_from, processed_at_to)
            for schema in SCHEMAS
        }

        result: list[pd.DataFrame] = []
        for schema, code in codes.items():
            time.sleep(TIME_SLEEP_CARDS_LINK)
            file_link = self.get_info_link(code)
            if not file_link:
                raise RuntimeError(f'Не удалось получить отчёт по заказам ({schema}), code={code}')
            orders = self.get_info_report(file_link)
            result.append(self.converter.convert_info(orders))

        combined = pd.concat(result, ignore_index=True)
        combined[self.orders_columns.created_at] = pd.to_datetime(combined[self.orders_columns.created_at])
        combined.sort_values(by=self.orders_columns.created_at, inplace=True)
        return combined

    @with_strategies(client_type='api',request_strategy=ReqReturnsInfoReportStrategy ,convert_strategy=ConvReturnsInfoStrategy)
    def get_returns(self, time_from: str, time_to: str):
        logger.info(f'Получение информации о возвратах (OZON)')
        returns = self.ozon_api_client.get_info(time_from=time_from, time_to=time_to)
        returns_df = self.converter.convert_info(returns)
        return returns_df

    @with_strategies(client_type='api', request_strategy=ReqOrdersInfoReportStrategy)
    def create_info_report_orders(self, schema: Literal['fbs', 'fbo'], processed_at_from: str, processed_at_to: str) -> str:
        logger.info(f'Создание отчета по заказам (OZON)')
        code = self.ozon_api_client.get_info(schema=schema, processed_at_from=processed_at_from, processed_at_to=processed_at_to)
        return code

    @with_strategies(client_type='api', request_strategy=ReqGetLinkStrategy)
    def get_info_link(self, code: str) -> str:
        logger.info(f'Получение ссылки на отчет (OZON)')
        file_link = self.ozon_api_client.get_info(code=code)
        return file_link

    @with_strategies(client_type='http', request_strategy=ReqGetLinkDataStrategy)
    def get_info_report(self, link: str) -> list[dict]:
        logger.info(f'Получение отчета (OZON)')
        orders_info = self.http_client.get_info(link=link)
        return orders_info

    @with_strategies(convert_strategy=ConvCardsInfoStrategy)
    def get_cards_info(self) -> pd.DataFrame:
        result: list[pd.DataFrame] = []
        for visibility in VISIBILITIES:
            code = self.create_info_report_cards(visibility=visibility)
            time.sleep(TIME_SLEEP_CARDS_LINK)
            file_link = self.get_info_link(code)
            if not file_link:
                raise RuntimeError(f'Не удалось получить отчёт по карточкам (visibility={visibility})')
            cards = self.get_info_report(file_link)
            cards_df = self.converter.convert_info(cards)
            result.append(cards_df)
        combined = pd.concat(result, ignore_index=True)
        return combined

    @with_strategies(client_type='api', request_strategy=ReqCardsInfoReportStrategy)
    def create_info_report_cards(self, visibility: str) -> str:
        logger.info('Запрос карточек')
        code = self.ozon_api_client.get_info(visibility=visibility)
        return code