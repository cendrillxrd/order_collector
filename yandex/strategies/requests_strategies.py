import time
from abc import ABC, abstractmethod

import requests

from logger import setup_logger
from yandex.yandex_config import (LIMIT_CARDS_INFO, LIMIT_ORDERS, LIMIT_PUBLISHED_CARDS,
                                  PURCHASE_LOGIN, PURCHASE_PASSWORD, TIME_SLEEP_CARDS_INFO,
                                  TIME_SLEEP_ORDERS, TIME_SLEEP_PUBLISHED_CARDS, LIMIT_RETURNS, YandexUrlKey, MedUrlKey)
from yandex.dto.request_yandex_config import RequestYandexConfig
from yandex.utils.date_helper import get_date_30_days_before_last_week_end, get_current_week_monday
from yandex.workers.client import Client, YandexAPIClient, MedClient

logger = setup_logger("my_app")

class RequestStrategy(ABC):
    @abstractmethod
    def do_request(self, client: Client, **kwargs) -> list[dict]:
        pass

class ReqYandexBusinessId(RequestStrategy):
    def do_request(self, client: YandexAPIClient, **kwargs) -> int:
        config = RequestYandexConfig(
            method='GET',
            url_key=YandexUrlKey.YANDEX,
            endpoint='/v2/campaigns',
            params={'page': 1},
        )
        response = client.make_request(config)
        return response['campaigns'][0]['business']['id']

class ReqYandexCampaignId(RequestStrategy):
    def do_request(self, client: YandexAPIClient, **kwargs) -> int:
        config = RequestYandexConfig(
            method='GET',
            url_key=YandexUrlKey.YANDEX,
            endpoint='/v2/campaigns',
            params={'page': 1},
        )
        response = client.make_request(config)
        return response['campaigns'][0]['id']

class ReqYandexReturns(RequestStrategy):
    def do_request(self, client: YandexAPIClient, **kwargs):
        """Обязательно передай campaign_id, date_from, date_to"""
        campaign_id = kwargs.get('campaign_id')
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        if not campaign_id:
            raise ValueError("campaign_id обязателен")
        if not date_from:
            raise ValueError("date_from обязателен")
        if not date_to:
            raise ValueError("date_to обязателен")

        config = RequestYandexConfig(
            method='GET',
            url_key=YandexUrlKey.YANDEX,
            endpoint=f'/v2/campaigns/{campaign_id}/returns',
            params={
                'limit': LIMIT_RETURNS,
                'type': 'RETURN',
                'fromDate': date_from,
                'toDate': date_to,
                'statuses': 'REFUNDED',
            },
        )

        result = []
        page_token = 'start_token'
        while page_token:
            if page_token != 'start_token':
                config.params['page_token'] = page_token
            time.sleep(TIME_SLEEP_ORDERS)
            response = client.make_request(config)
            page_token = response['result']['paging'].get('nextPageToken')
            result.extend(response['result']['returns'])
            logger.info(f'Загружено возвратов: {len(result)}')
        return result

class ReqYandexOrders(RequestStrategy):
    def do_request(self, client: YandexAPIClient, **kwargs) -> list[dict]:
        business_id = kwargs.get('business_id')
        if not business_id:
            raise ValueError("business_id обязателен")

        config = RequestYandexConfig(
            method='POST',
            url_key=YandexUrlKey.YANDEX,
            endpoint=f'/v1/businesses/{business_id}/orders',
            params={'limit': LIMIT_ORDERS},
            payload={
                'fake': False,
                'dates': {
                    'creationDateFrom': get_date_30_days_before_last_week_end(),
                    'creationDateTo': get_current_week_monday(),
                },
            },
        )

        result = []
        page_token = 'start_token'
        while page_token:
            if page_token != 'start_token':
                config.params['page_token'] = page_token
            time.sleep(TIME_SLEEP_ORDERS)
            response = client.make_request(config)
            page_token = response['paging'].get('nextPageToken')
            result.extend(response['orders'])
            logger.info(f'Загружено заказов: {len(result)}')
        return result

class ReqMEDCollections(RequestStrategy):
    def __init__(self, url_key: MedUrlKey):
        self.url_key = url_key

    def do_request(self, client: MedClient, **kwargs) -> requests.Response:
        config = RequestYandexConfig(
            method='GET',
            url_key=self.url_key,
            endpoint='',
        )
        return client.make_request(config)