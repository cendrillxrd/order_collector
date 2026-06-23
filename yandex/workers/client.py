import time
from abc import ABC, abstractmethod
from typing import Union, Dict

import requests

from logger import setup_logger
from yandex.config import API_KEY_YANDEX, RETRYABLE_STATUS_CODES, MAX_WAIT_SECONDS, YANDEX_BASE_URLS, \
    MED_BASE_URLS
from yandex.dto.request_yandex_config import RequestYandexConfig

logger = setup_logger("my_app")


class Client(ABC):
    @abstractmethod
    def make_request(self, config: RequestYandexConfig):
        pass


class YandexAPIClient(Client):
    def __init__(
        self,
        retries: int = 5,
        base_urls: Dict[str, str] = YANDEX_BASE_URLS,
        api_key: str = API_KEY_YANDEX,
    ):
        self.base_urls = base_urls
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({
            'Api-Key': api_key,
            'Content-Type': 'application/json',
        })

    def make_request(self, config: RequestYandexConfig):
        url = f'{self.base_urls[config.url_key]}{config.endpoint}'
        logger.info(f'Выполнение запроса по адресу {url}')

        for attempt in range(self.retries):
            try:
                response = self.session.request(
                    method=config.method,
                    url=url,
                    params=config.params,
                    json=config.payload,
                    timeout=30,
                )
                logger.info(
                    f'Запрос выполнен (попытка {attempt + 1}/{self.retries}), '
                    f'статус: {response.status_code}'
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as err:
                status = err.response.status_code if err.response else None
                logger.warning(f'HTTP ошибка {status}')
                if not self._should_retry(attempt) or status not in RETRYABLE_STATUS_CODES:
                    raise
                self._wait_before_retry(attempt, f'HTTP ошибка {status}')

            except requests.exceptions.RequestException as err:
                logger.warning(f'Ошибка запроса: {err}')
                if not self._should_retry(attempt):
                    raise
                self._wait_before_retry(attempt, 'ошибка соединения')

        return None

    def _should_retry(self, attempt: int) -> bool:
        return attempt < self.retries - 1

    @staticmethod
    def _wait_before_retry(attempt: int, reason: str) -> None:
        wait_time = min(2 ** attempt, MAX_WAIT_SECONDS)
        logger.info(f'Повтор через {wait_time} сек. (причина: {reason})')
        time.sleep(wait_time)


class MedClient(Client):
    def __init__(self, base_urls: dict = MED_BASE_URLS):
        self.base_urls = base_urls

    def make_request(self, config: RequestYandexConfig) -> requests.Response:
        url = self.base_urls[config.url_key]
        response = requests.get(url)
        response.raise_for_status()
        return response