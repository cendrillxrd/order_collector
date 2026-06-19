import time
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import timedelta, datetime

from logger import setup_logger
from wb.dto.request_wb_config import RequestWBConfig
from wb.wb_config import TIME_SLEEP_ORDERS, TIME_SLEEP_SALES, ApiType, WBUrlKey
from wb.workers.clients import Client

logger = setup_logger("my_app")

class RequestStrategy(ABC):
    @abstractmethod
    def do_request(self, client: Client, *args, **kwargs) -> list[dict]:
        pass

class ReqOrdersStrategy(RequestStrategy):
    def do_request(self, client: Client, *args, **kwargs) -> list[dict]:
        """Обязательно передай date_from и date_to"""
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')

        if not date_from:
            raise ValueError("date_from обязателен")
        if not date_to:
            raise ValueError("date_to обязателен")

        if isinstance(date_from, str):
            current_date = datetime.strptime(date_from, '%Y-%m-%d')
        else:
            current_date = date_from

        if isinstance(date_to, str):
            end_date = datetime.strptime(date_to, '%Y-%m-%d')
        else:
            end_date = date_to

        all_results = []

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            logger.info(f'Получение информации о заказах {date_str} (WB)')
            params = {'flag': 1, 'dateFrom': date_str}
            config = RequestWBConfig(
                method='GET',
                api_type=ApiType.STATISTICS,
                url_key=WBUrlKey.STATISTICS,
                endpoint='/api/v1/supplier/orders',
                params=params,
            )
            response = client.make_request(config)

            all_results.extend(response)

            if current_date < end_date:
                time.sleep(TIME_SLEEP_ORDERS)

            current_date += timedelta(days=1)

        return all_results

class ReqSalesStrategy(RequestStrategy):
    def do_request(self, client: Client, *args, **kwargs) -> list[dict]:
        """Обязательно передай date_from и date_to"""
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')

        if not date_from:
            raise ValueError("date_from обязателен")
        if not date_to:
            raise ValueError("date_to обязателен")

        if isinstance(date_from, str):
            current_date = datetime.strptime(date_from, '%Y-%m-%d')
        else:
            current_date = date_from

        if isinstance(date_to, str):
            end_date = datetime.strptime(date_to, '%Y-%m-%d')
        else:
            end_date = date_to

        all_results = []

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            logger.info(f'Получение информации о продажах {date_str} (WB)')

            params = {'flag': 1, 'dateFrom': date_str}

            config = RequestWBConfig(
                method='GET',
                api_type=ApiType.STATISTICS,
                url_key=WBUrlKey.STATISTICS,
                endpoint='/api/v1/supplier/sales',
                params=params,
            )
            response = client.make_request(config)

            all_results.extend(response)

            if current_date < end_date:
                time.sleep(TIME_SLEEP_SALES)

            current_date += timedelta(days=1)

        return all_results