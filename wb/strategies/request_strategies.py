import time
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import timedelta, datetime

from logger import setup_logger
from wb.config import TIME_SLEEP_ORDERS, TIME_SLEEP_SALES
from wb.dto.orders_dto import OrdersDTO
from wb.dto.sales_dto import SalesDTO

logger = setup_logger("my_app")

class RequestStrategy(ABC):
    @abstractmethod
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        pass

class ReqOrdersStrategy(RequestStrategy):
    endpoint = '/api/v1/supplier/orders'
    api_type = 'Analytics_Statistics_API_KEY'
    url_key = 'statistics'
    orders_dto = OrdersDTO()

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
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
            params = asdict(self.orders_dto)
            params['dateFrom'] = date_str

            response = client.make_request(
                method='GET',
                api_type=self.api_type,
                url_key=self.url_key,
                endpoint=self.endpoint,
                params=params
            )

            all_results.extend(response)

            if current_date < end_date:
                time.sleep(TIME_SLEEP_ORDERS)

            current_date += timedelta(days=1)

        return all_results

class ReqSalesStrategy(RequestStrategy):
    endpoint = '/api/v1/supplier/sales'
    api_type = 'Analytics_Statistics_API_KEY'
    url_key = 'statistics'
    sales_dto = SalesDTO()

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
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

            params = asdict(self.sales_dto)
            params['dateFrom'] = date_str

            response = client.make_request(
                method='GET',
                api_type=self.api_type,
                url_key=self.url_key,
                endpoint=self.endpoint,
                params=params
            )

            all_results.extend(response)

            if current_date < end_date:
                time.sleep(TIME_SLEEP_SALES)

            current_date += timedelta(days=1)

        return all_results