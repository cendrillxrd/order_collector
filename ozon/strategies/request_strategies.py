import time
from abc import ABC, abstractmethod

from logger import setup_logger
from ozon.dto.request_http_config import RequestHTTPConfig
from ozon.dto.request_ozon_config import RequestOZONConfig
from ozon.ozon_config import TIME_SLEEP_REPORT, TIME_SLEEP_RETURNS, OZONUrlKey, MAX_GET_CODE_ATTEMPTS, LIMIT_RETURNS
from ozon.workers.clients import Client

logger = setup_logger("my_app")

class RequestStrategy(ABC):
    @abstractmethod
    def do_request(self, client: Client, *args, **kwargs) -> list[dict] | str | None:
        pass

class ReqGetLinkStrategy(RequestStrategy):
    def do_request(self, client: Client, *args, **kwargs) -> str | None:
        """Обязательно передай code"""
        code = kwargs.get('code')
        if not code:
            raise ValueError("code обязателен")

        payload = {'code': code}
        config = RequestOZONConfig(
            method='POST',
            url_key=OZONUrlKey.OZON,
            endpoint='/v1/report/info',
            payload=payload,
        )

        for attempt in range(MAX_GET_CODE_ATTEMPTS):
            response = client.make_request(config)
            status = response['result']['status']

            if status == 'success':
                return response['result']['file']

            if status not in ('waiting', 'processing'):
                return None

            logger.info(f'Отчёт ещё не готов (статус: {status}), попытка {attempt + 1}/{MAX_GET_CODE_ATTEMPTS}')
            time.sleep(TIME_SLEEP_REPORT)

        logger.warning(f'Отчёт не готов после {MAX_GET_CODE_ATTEMPTS} попыток')
        return None

class ReqOrdersInfoReportStrategy(RequestStrategy):
    def do_request(self, client: Client, *args, **kwargs) -> str:
        """Обязательные kwargs: schema, processed_at_from, processed_at_to"""

        schema = kwargs.get('schema')
        processed_at_from = kwargs.get('processed_at_from')
        processed_at_to = kwargs.get('processed_at_to')
        if not schema:
            raise ValueError("schema обязателен")
        if not processed_at_from:
            raise ValueError("processed_at_from обязателен")
        if not processed_at_to:
            raise ValueError("processed_at_to обязателен")

        payload = {'filter': {
            "processed_at_from": processed_at_from,
            "processed_at_to": processed_at_to,
            "delivery_schema": [schema],
            "sku": [],
            "cancel_reason_id": [],
            "offer_id": "",
            "status_alias": [],
            "statuses": [],
            "title": ""
            }
        }

        config = RequestOZONConfig(
            method='POST',
            url_key=OZONUrlKey.OZON,
            endpoint='/v1/report/postings/create',
            payload=payload,
        )
        response = client.make_request(config)
        code = response['result']['code']
        return code

class ReqReturnsInfoReportStrategy(RequestStrategy):
    def do_request(self, client: Client, *args, **kwargs) -> list[dict]:
        """Обязательные kwargs: time_from, time_to"""
        time_from = kwargs.get('time_from')
        time_to = kwargs.get('time_to')
        if not time_from:
            raise ValueError("time_from обязателен")
        if not time_to:
            raise ValueError("time_to обязателен")

        payload = {
            'filter': {
                "logistic_return_date": {
                "time_from": time_from,
                "time_to": time_to
                },
            } ,
            'limit': LIMIT_RETURNS,
        }

        result = []
        has_next = True
        while has_next:
            config = RequestOZONConfig(
                method='POST',
                url_key=OZONUrlKey.OZON,
                endpoint='/v1/returns/list',
                payload=payload,
            )
            response = client.make_request(config)
            has_next = response['has_next']
            if has_next:
                payload['last_id'] = response['returns'][-1]['id']
                time.sleep(TIME_SLEEP_RETURNS)
            result.extend(response['returns'])
            logger.info(f'Получено {len(result)}, есть ещё: {has_next}')
        return result

class ReqCardsInfoReportStrategy(RequestStrategy):
    def do_request(self, client: Client, *args, **kwargs) -> str:
        """Обязательные kwargs: visibility"""
        visibility = kwargs.get('visibility')
        if visibility is None:
            raise ValueError('visibility is required')

        payload = {'visibility': visibility}

        config = RequestOZONConfig(
            method='POST',
            url_key=OZONUrlKey.OZON,
            endpoint='/v1/report/products/create',
            payload=payload,
        )

        response = client.make_request(config)
        code = response['result']['code']
        return code

class ReqGetLinkDataStrategy(RequestStrategy):
    def do_request(self, client: Client, *args, **kwargs) -> list[dict]:
        """Обязательные kwargs: link"""
        link = kwargs.get('link')
        if link is None:
            raise ValueError('link is required')

        config = RequestHTTPConfig(
            url_key=OZONUrlKey.HTTP,
            endpoint=str(link),
        )

        response = client.make_request(config)
        return response