import time
from abc import ABC, abstractmethod
from dataclasses import asdict

from lamoda.lamoda_config import (TIME_SLEEP_ORDER,
                                  TIME_SLEEP_ORDER_INFO, TIME_SLEEP_NOMENCLATURES, )
from lamoda.dto.nomenclature_dto import NomenclatureDTO
from lamoda.dto.order_dto import OrderDTO
from lamoda.utils.create_id_helper import generate_uuid_id
from logger import setup_logger

logger = setup_logger("my_app")


class RequestStrategy(ABC):
    @abstractmethod
    def get_info(self, client: 'APIClient', **kwargs) -> list[dict]:
        pass

class ReqFullNomenclatureStrategy(RequestStrategy):
    endpoint = '/jsonrpc/v1/nomenclatures.list'
    method = 'v1.nomenclatures.list'
    url_key = 'b2b'
    nomenclature_dto = NomenclatureDTO()
    nomenclature_dto.method = method

    def get_info(self, client: 'APIClient', **kwargs) -> list[dict]:
        logger.info('Запрос номенклатуры')
        result = []
        skus = kwargs.get('skus')
        payload = asdict(self.nomenclature_dto)
        payload['id'] = generate_uuid_id()
        payload['params']['filter'][0]['value'] = skus
        response = client.make_request(method='POST',
                                       url_key=self.url_key,
                                       payload=payload,
                                       endpoint=self.endpoint)
        result.extend(response['result']['nomenclatures'])
        pages = response['result']['pages']
        payload['id'] = generate_uuid_id()
        logger.info(f'Всего страниц: {pages}')
        logger.info(f'Загружено страниц: {self.nomenclature_dto.params['page']}')

        for page in range(self.nomenclature_dto.params['page'] + 1, pages + 1):
            time.sleep(TIME_SLEEP_NOMENCLATURES)
            payload['params']['page'] = page
            logger.info( f'Загружено страниц: {page}')
            response = client.make_request(method='POST',
                                           url_key=self.url_key,
                                           payload=payload,
                                           endpoint=self.endpoint)
            result.extend(response['result']['nomenclatures'])
        return result

class ReqOrdersStrategy(RequestStrategy):
    endpoint = '/api/v1/orders'
    url_key = 'live'

    def get_info(self, client: 'APIClient', start_date: str = None, end_date: str = None, **kwargs) -> list[
        dict]:
        """
        Получает заказы за указанный период

        Args:
            client: APIClient экземпляр
            start_date: Начальная дата (str с таймзоной)
            end_date: Конечная дата (str с таймзоной)
            **kwargs: Дополнительные параметры

        Returns:
            list[dict]: Список заказов
        """
        logger.info(f'Запрос заказов за период: {start_date} - {end_date}')
        result = []

        if start_date is not None and end_date is not None:
            order_dto = OrderDTO.with_date_range(start_date, end_date)
        else:
            order_dto = OrderDTO()

        params = asdict(order_dto)
        # Убираем filter если он None
        if params.get('filter') is None:
            del params['filter']

        response = client.make_request(method='GET',
                                       url_key=self.url_key,
                                       params=params,
                                       endpoint=self.endpoint)
        result.extend(response['_embedded']['orders'])
        pages = response['pages']
        logger.info(f'Всего страниц: {pages}')
        logger.info(f'Загружено страниц: {order_dto.page}')

        for page in range(order_dto.page + 1, pages + 1):
            time.sleep(TIME_SLEEP_ORDER)
            logger.info(f'Загружено страниц: {page}')
            params['page'] = page
            response = client.make_request(method='GET',
                                           url_key=self.url_key,
                                           params=params,
                                           endpoint=self.endpoint)
            result.extend(response['_embedded']['orders'])
        return result


class ReqOrderInfoStrategy(RequestStrategy):
    endpoint = '/api/v1/orders'
    url_key = 'live'

    def get_info(self, client: 'APIClient', **kwargs) -> list[dict]:
        logger.info(f'Запрос подробной информации о заказе {kwargs['order_id']}')
        endpoint = f'{self.endpoint}/{kwargs['order_id']}'
        time.sleep(TIME_SLEEP_ORDER_INFO)
        response = client.make_request(method='GET',
                                       url_key=self.url_key,
                                       endpoint=endpoint)

        return response


class ReqMEDCollectionsFirst(RequestStrategy):
    url_key = "med_collections_1"

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        logger.info('Получение первого файла коллекций')
        response = client.make_request(url_key=self.url_key)
        return response


class ReqMEDCollectionsThird(RequestStrategy):
    url_key = "med_collections_3"

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        logger.info('Получение третьего файла коллекций')
        response = client.make_request(url_key=self.url_key)
        return response


class ReqMEDCollectionsFourth(RequestStrategy):
    url_key = "med_collections_4"

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        logger.info('Получение четвертого файла коллекций')
        response = client.make_request(url_key=self.url_key)
        return response


class ReqMEDCollectionsSecond(RequestStrategy):
    url_key = "med_collections_2"

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        logger.info('Получение второго файла коллекций')
        response = client.make_request(url_key=self.url_key)
        return response
