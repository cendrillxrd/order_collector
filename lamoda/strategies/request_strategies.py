import time
from abc import ABC, abstractmethod
from dataclasses import asdict

from lamoda.dto.request_lamoda_config import RequestLamodaConfig
from lamoda.lamoda_config import (TIME_SLEEP_ORDER,
                                  TIME_SLEEP_ORDER_INFO, TIME_SLEEP_NOMENCLATURES, LamodaUrlKey, MedUrlKey, )
from lamoda.dto.nomenclature_dto import NomenclatureDTO
from lamoda.dto.order_dto import OrderDTO
from lamoda.utils.create_id_helper import generate_uuid_id
from lamoda.workers.api_client import APIClient, Client
from logger import setup_logger

logger = setup_logger("my_app")


class RequestStrategy(ABC):
    @abstractmethod
    def get_info(self, client: Client, **kwargs):
        pass


class ReqFullNomenclatureStrategy(RequestStrategy):
    def get_info(self, client: APIClient, **kwargs) -> list[dict]:
        logger.info('Запрос номенклатуры')
        skus = kwargs.get('skus')
        if not skus:
            raise ValueError("skus обязателен")

        nomenclature_dto = NomenclatureDTO()
        nomenclature_dto.method = 'v1.nomenclatures.list'
        payload = asdict(nomenclature_dto)
        payload['id'] = generate_uuid_id()
        payload['params']['filter'][0]['value'] = skus

        config = RequestLamodaConfig(
            method='POST',
            url_key=LamodaUrlKey.B2B,
            endpoint='/jsonrpc/v1/nomenclatures.list',
            payload=payload,
        )

        response = client.make_request(config)
        result = list(response['result']['nomenclatures'])
        pages = response['result']['pages']
        logger.info(f'Всего страниц: {pages}')

        for page in range(2, pages + 1):
            time.sleep(TIME_SLEEP_NOMENCLATURES)
            payload['params']['page'] = page
            payload['id'] = generate_uuid_id()
            response = client.make_request(config)
            try:
                nomenclatures = response['result']['nomenclatures']
            except KeyError:
                logger.info(f'Плохой ответ от сервера {response}')
                continue
            result.extend(nomenclatures)
            logger.info(f'Загружено страниц: {page}/{pages}')

        return result

class ReqOrdersStrategy(RequestStrategy):
    def get_info(self, client: APIClient, **kwargs) -> list[dict]:
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        if not start_date:
            raise ValueError("start_date обязателен")
        if not end_date:
            raise ValueError("end_date обязателен")

        logger.info(f'Запрос заказов: {start_date} — {end_date}')

        order_dto = (
            OrderDTO.with_date_range(str(start_date), str(end_date))
            if start_date and end_date
            else OrderDTO()
        )
        params = asdict(order_dto)
        if params.get('filter') is None:
            del params['filter']

        config = RequestLamodaConfig(
            method='GET',
            url_key=LamodaUrlKey.LIVE,
            endpoint='/api/v1/orders',
            params=params,
        )

        response = client.make_request(config)
        result = list(response['_embedded']['orders'])
        pages = response['pages']
        logger.info(f'Всего страниц: {pages}')

        for page in range(2, pages + 1):
            time.sleep(TIME_SLEEP_ORDER)
            config.params['page'] = page
            response = client.make_request(config)
            result.extend(response['_embedded']['orders'])
            logger.info(f'Загружено страниц: {page}/{pages}')

        return result


class ReqOrderInfoStrategy(RequestStrategy):
    def get_info(self, client: APIClient, **kwargs):
        order_id = kwargs.get('order_id')
        if not order_id:
            raise ValueError("order_id обязателен")

        logger.info(f'Запрос информации о заказе {order_id}')
        time.sleep(TIME_SLEEP_ORDER_INFO)

        config = RequestLamodaConfig(
            method='GET',
            url_key=LamodaUrlKey.LIVE,
            endpoint=f'/api/v1/orders/{order_id}',
        )
        return client.make_request(config)