import time
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Union

from logger import setup_logger
from ozon.config import TIME_SLEEP_REPORT, TIME_SLEEP_RETURNS
from ozon.dto.orders_dto import OrdersDTO
from ozon.dto.returned_dto import ReturnedDTO
logger = setup_logger("my_app")

class RequestStrategy(ABC):
    @abstractmethod
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        pass

class ReqGetLinkStrategy(RequestStrategy):
    endpoint = '/v1/report/info'
    url_key = 'ozon'

    def get_info(self, client: 'Client', **kwargs) -> Union[list[dict], bool]:
        # log_message('app', 'Получение ссылки', 'INFO')
        payload = {'code': kwargs['code']}
        response = client.make_request(method='POST',
                                       url_key=self.url_key,
                                       payload=payload,
                                       endpoint=self.endpoint)
        status = response['result']['status']
        if status == 'success':
            file_link = response['result']['file']
            return file_link
        elif status in ('waiting', 'processing'):
            time.sleep(TIME_SLEEP_REPORT)
            return self.get_info(client, code=kwargs['code'])
        return False

class ReqOrdersInfoReportStrategy(RequestStrategy):
    endpoint = '/v1/report/postings/create'
    url_key = 'ozon'
    orders_dto = OrdersDTO()
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        schema = kwargs.get('schema')
        payload = asdict(self.orders_dto)
        payload['filter']['delivery_schema'] = [schema]
        # log_message('app', 'Запрос заказов', 'INFO')
        response = client.make_request(method='POST',
                                       url_key=self.url_key,
                                       endpoint=self.endpoint,
                                       payload=payload)
        code = response['result']['code']
        return code

class ReqReturnsInfoReportStrategy(RequestStrategy):
    endpoint = '/v1/returns/list'
    url_key = 'ozon'
    returned_dto = ReturnedDTO()
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        # schema = kwargs.get('schema')
        payload = asdict(self.returned_dto)
        # payload['filter']['delivery_schema'] = schema
        result = []
        has_next = True
        while has_next:
            time.sleep(TIME_SLEEP_RETURNS)
            response = client.make_request(method='POST',
                                           url_key=self.url_key,
                                           endpoint=self.endpoint,
                                           payload=payload)
            has_next = response['has_next']
            if has_next:
                payload['last_id'] = response['returns'][-1]['id']
            result.extend(response['returns'])
            logger.info(f'Получено {len(result)}')
        return result

class ReqCardsInfoReportStrategy(RequestStrategy):
    endpoint = '/v1/report/products/create'
    url_key = 'ozon'

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        logger.info('Запрос карточек')
        visibility = kwargs.get('visibility')
        if visibility is None:
            raise ValueError('visibility is required')
        payload = {'visibility': visibility}
        response = client.make_request(method='POST',
                                       url_key=self.url_key,
                                       payload=payload,
                                       endpoint=self.endpoint)
        code = response['result']['code']
        return code

class ReqGetLinkDataStrategy(RequestStrategy):
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        # log_message('app', 'Получение данных из ссылки', 'INFO')
        link = kwargs['link']
        response = client.make_request(url=link)
        return response

class ReqCollectionsFirstMEDStrategy(RequestStrategy):
    url_key = "med_collections_1"
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        response = client.make_request(url_key=self.url_key)
        return response

class ReqCollectionsSecondMEDStrategy(RequestStrategy):
    url_key = "med_collections_2"
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        response = client.make_request(url_key=self.url_key)
        return response

class ReqCollectionsThirdMEDStrategy(RequestStrategy):
    url_key = "med_collections_3"
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        response = client.make_request(url_key=self.url_key)
        return response

class ReqCollectionsFourthMEDStrategy(RequestStrategy):
    url_key = "med_collections_4"
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        response = client.make_request(url_key=self.url_key)
        return response
