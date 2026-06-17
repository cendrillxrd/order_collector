import time
from abc import ABC, abstractmethod

import requests
from typing import Dict

from logger import setup_logger
from wb.dto.request_config import RequestConfig
from wb.wb_config import BASE_URLS, API_KEYS, RETRYABLE_STATUS_CODES, MAX_WAIT_SECONDS

logger = setup_logger("my_app")

class Client(ABC):
    @abstractmethod
    def make_request(self, config: RequestConfig):
        pass

class WildberriesAPIClient(Client):
    def __init__(self, retries: int = 5, base_urls: Dict[str, str] = BASE_URLS, api_keys: Dict[str, str] = API_KEYS):
        self.base_urls = base_urls
        self.api_keys = api_keys
        self.retries = retries
        self.session = requests.Session()

    def make_request(self, config: RequestConfig):
        url = f'{self.base_urls[config.url_key]}{config.endpoint}'
        logger.info(f'Выполнение запроса по адресу {url}')

        self.session.headers.update({
            'Authorization': self.api_keys[config.api_type],
            'Content-Type': 'application/zip' if config.zip_needs else 'application/json',
        })

        for attempt in range(self.retries):
            try:
                response = self.session.request(
                    method=config.method,
                    url=url,
                    params=config.params,
                    json=config.payload,
                    timeout=30,
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
        wait_time = min(2 ** attempt, MAX_WAIT_SECONDS)
        logger.info(f'Повтор через {wait_time} сек. (причина: {reason})')
        time.sleep(wait_time)