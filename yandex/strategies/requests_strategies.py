import time
from abc import ABC, abstractmethod

from logger import setup_logger
from yandex.config import (LIMIT_CARDS_INFO, LIMIT_ORDERS, LIMIT_PUBLISHED_CARDS,
                           PURCHASE_LOGIN, PURCHASE_PASSWORD, TIME_SLEEP_CARDS_INFO,
                           TIME_SLEEP_ORDERS, TIME_SLEEP_PUBLISHED_CARDS, LIMIT_RETURNS)
from yandex.utils.date_helper import get_date_30_days_after_last_week_end, get_current_week_monday
logger = setup_logger("my_app")

class RequestStrategy(ABC):
    @abstractmethod
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        pass

class ReqYandexReturns(RequestStrategy):
    endpoint = '/v2/campaigns/{campaignId}/returns'

    def get_info(self, client: 'Client', **kwargs):
        """Обязательно передай campaign_id, date_from, date_to"""
        # logger.info(f'Получение информации о заказах')
        result = []
        campaign_id = kwargs.get('campaign_id')
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        if not campaign_id:
            raise ValueError("campaign_id обязателен")
        endpoint = self.endpoint.format(campaignId=campaign_id)

        params = {'limit': LIMIT_RETURNS,
                  'type': 'RETURN',
                  'fromDate': date_from,
                  'toDate': date_to,
                  'statuses': 'REFUNDED'}

        count = 0

        page_token = 'start_token'
        while page_token:
            if page_token != 'start_token':
                params['page_token'] = page_token
            time.sleep(TIME_SLEEP_ORDERS)

            response = client.make_request(method='GET',
                                           params=params,
                                           endpoint=endpoint)
            page_token = response['result']['paging'].get('nextPageToken')
            returns = response['result']['returns']

            result.extend(returns)

            count += len(returns)
            logger.info(f'Загружено возвратов {count}')
        return result

class ReqYandexOrders(RequestStrategy):
    endpoint = '/v1/businesses/{businessId}/orders'

    def get_info(self, client: 'Client', **kwargs):
        """Обязательно передай business_id"""
        # logger.info(f'Получение информации о заказах')
        result = []

        business_id = kwargs.get('business_id')
        if not business_id:
            raise ValueError("business_id обязателен")
        endpoint = self.endpoint.format(businessId=business_id)

        params = {'limit': LIMIT_ORDERS}
        json = {'fake': False,
                "dates": {
                    "creationDateFrom": get_date_30_days_after_last_week_end(),
                    "creationDateTo": get_current_week_monday(),
                }
                }

        count = 0

        page_token = 'start_token'
        while page_token:
            if page_token != 'start_token':
                params['page_token'] = page_token
            time.sleep(TIME_SLEEP_ORDERS)

            response = client.make_request(method='POST',
                                           params=params,
                                           json=json,
                                           endpoint=endpoint)
            page_token = response['paging'].get('nextPageToken')
            orders = response['orders']

            result.extend(orders)

            count += len(orders)
            # logger.debug(f'Загружено заказов {count}')
            if count % 100 == 0:
                pass
                # logger.info(f'Загружено заказов {count}')
        return result

class ReqMEDCollectionsFirst(RequestStrategy):
    url_key = "med_collections_1"

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        # logger.info(f'Получение первого файла коллекций')
        response = client.make_request(url_key=self.url_key)
        return response

class ReqMEDCollectionsSecond(RequestStrategy):
    url_key = "med_collections_2"

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        # logger.info(f'Получение второго файла коллекций')
        response = client.make_request(url_key=self.url_key)
        return response

class ReqMEDCollectionsThird(RequestStrategy):
    url_key = "med_collections_3"

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        # logger.info(f'Получение третьего файла коллекций')
        response = client.make_request(url_key=self.url_key)
        return response

class ReqMEDCollectionsFourth(RequestStrategy):
    url_key = "med_collections_4"

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        # logger.info(f'Получение четвертого файла коллекций')
        response = client.make_request(url_key=self.url_key)
        return response

class ReqYandexBusinessId(RequestStrategy):
    endpoint = '/v2/campaigns'

    def get_info(self, client: 'Client', **kwargs) -> int:
        # logger.info(f'Получение BusinessId')
        params = {'page': 1}
        response = client.make_request(method='GET',
                            params=params,
                            endpoint=self.endpoint)
        return response['campaigns'][0]['business']['id']

class ReqYandexCampaignId(RequestStrategy):
    endpoint = '/v2/campaigns'

    def get_info(self, client: 'Client', **kwargs) -> int:
        # logger.info(f'Получение BusinessId')
        params = {'page': 1}
        response = client.make_request(method='GET',
                            params=params,
                            endpoint=self.endpoint)
        return response['campaigns'][0]['id']