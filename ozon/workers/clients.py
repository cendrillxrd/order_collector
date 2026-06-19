import random
from abc import ABC, abstractmethod

from logger import setup_logger
from ozon.dto.request_http_config import RequestHTTPConfig
from ozon.dto.request_ozon_config import RequestOZONConfig
from ozon.ozon_config import API_KEY, BASE_URLS, CLIENT_ID, MAX_WAIT_SECONDS, RETRYABLE_STATUS_CODES, OZONUrlKey
import time
import requests
from typing import Dict

logger = setup_logger("my_app")

class Client(ABC):
    @abstractmethod
    def make_request(self, config):
        pass

class OzonAPIClient(Client):
    def __init__(
        self,
        retries: int = 5,
        base_urls: Dict[OZONUrlKey, str] = BASE_URLS,
        client_id: str = CLIENT_ID,
        api_key: str = API_KEY,
    ):
        self.base_urls = base_urls
        self.client_id = client_id
        self.api_key = api_key
        self.retries = retries
        self.session = requests.Session()

    def make_request(self, config: RequestOZONConfig):
        url = f'{self.base_urls[config.url_key]}{config.endpoint}'
        logger.info(f'Выполнение запроса по адресу {url}')

        self.session.headers.update({
            'Client-Id': self.client_id,
            'Api-Key': self.api_key,
            'Content-Type': 'application/zip' if config.zip_needs else 'application/json',
        })

        for attempt in range(self.retries):
            try:
                response = self.session.request(
                    method=config.method,
                    url=url,
                    params=config.params,
                    json=config.payload,
                    timeout=(30, 60),
                )
                logger.info(f'Запрос выполнен (попытка {attempt + 1}/{self.retries}), статус: {response.status_code}')
                response.raise_for_status()

                return response if config.zip_needs else response.json()

            except requests.exceptions.JSONDecodeError as err:
                logger.warning(f'JSON ошибка (попытка {attempt + 1}/{self.retries}): {err}')
                if not self._should_retry(attempt):
                    raise
                self._wait_before_retry(attempt, 'JSON ошибка')

            except requests.exceptions.HTTPError as err:
                status = err.response.status_code if err.response else 'Unknown'
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
        wait_time = min(2 ** attempt + random.uniform(0.1, 0.5), MAX_WAIT_SECONDS)
        logger.info(f'Повтор через {wait_time:.1f} сек. (причина: {reason})')
        time.sleep(wait_time)

class HttpClient(Client):
    def __init__(self, base_urls: Dict[OZONUrlKey, str] = BASE_URLS):
        self.base_urls = base_urls

    def make_request(self, config: RequestHTTPConfig):
        url = f'{self.base_urls[config.url_key]}{config.endpoint}'
        logger.info(f'Выполнение запроса по адресу {url}')
        response = requests.get(url, timeout=(120, 120))
        return response