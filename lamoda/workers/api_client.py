import time
from abc import ABC, abstractmethod

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from lamoda.dto.request_lamoda_config import RequestLamodaConfig
from lamoda.lamoda_config import (
    BASE_URLS, MED_BASE_URLS, LamodaUrlKey, MedUrlKey,
    RETRYABLE_STATUS_CODES, MAX_WAIT_SECONDS,
)
from logger import setup_logger

logger = setup_logger("my_app")


class Client(ABC):
    @abstractmethod
    def make_request(self, *args, **kwargs):
        pass


class APIClient(Client):
    def __init__(
        self,
        api_key_manager: 'ApiKeyManager' = None,
        retries: int = 5,
        base_urls: dict[LamodaUrlKey, str] = BASE_URLS,
    ):
        self.base_urls = base_urls
        self.retries = retries
        self.api_key_manager = api_key_manager

        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=list(RETRYABLE_STATUS_CODES),
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update({'Content-Type': 'application/json'})
        self._refresh_auth_header()

    def _refresh_auth_header(self) -> None:
        if self.api_key_manager:
            try:
                key = self.api_key_manager.get_key()
                self.session.headers.update({'Authorization': f'Bearer {key}'})
            except Exception as e:
                logger.warning(f'Не удалось получить API ключ: {e}')
                self.session.headers.pop('Authorization', None)
        else:
            self.session.headers.pop('Authorization', None)

    def make_request(self, config: RequestLamodaConfig):
        url = f'{self.base_urls[config.url_key]}{config.endpoint}'
        logger.info(f'Запрос: {config.method} {url}')

        for attempt in range(self.retries):
            try:
                response = self.session.request(
                    method=config.method,
                    url=url,
                    params=config.params,
                    json=config.payload,
                    timeout=(30, 30),
                )
                logger.info(
                    f'Ответ (попытка {attempt + 1}/{self.retries}): '
                    f'статус {response.status_code}'
                )

                if response.status_code == 401:
                    self._handle_unauthorized(attempt)
                    continue

                if response.status_code in RETRYABLE_STATUS_CODES:
                    self._wait_before_retry(attempt, f'HTTP {response.status_code}')
                    continue

                response.raise_for_status()

                if 'application/zip' in response.headers.get('Content-Type', ''):
                    return response

                data = response.json()

                if (
                        isinstance(data, dict)
                        and data.get('error', {}).get('message') == 'invalid_grant'
                ):
                    logger.warning('invalid_grant в теле ответа — обновляем токен')
                    self._handle_unauthorized(attempt)
                    continue

                return data

            except requests.exceptions.ReadTimeout:
                self._wait_before_retry(attempt, 'таймаут чтения')
            except requests.exceptions.ConnectTimeout:
                self._wait_before_retry(attempt, 'таймаут подключения')
            except requests.exceptions.ConnectionError:
                self._wait_before_retry(attempt, 'ошибка соединения')
            except requests.exceptions.HTTPError as err:
                logger.warning(f'HTTP ошибка: {err}')
                if not self._should_retry(attempt):
                    raise
                self._wait_before_retry(attempt, str(err))
            except requests.exceptions.RequestException as err:
                logger.warning(f'Ошибка запроса: {err}')
                if not self._should_retry(attempt):
                    raise
                self._wait_before_retry(attempt, str(err))

        raise Exception(f'Превышено количество попыток ({self.retries}) для {url}')

    def _handle_unauthorized(self, attempt: int) -> None:
        logger.warning('401 Unauthorized — попытка обновить токен')
        if not self.api_key_manager:
            raise Exception('401 Unauthorized и нет менеджера ключей')
        try:
            self.api_key_manager.force_renew()
            self._refresh_auth_header()
            logger.info('Токен обновлён, повтор через 10 сек.')
        except Exception as e:
            logger.error(f'Ошибка обновления токена: {e}')
            raise
        time.sleep(10)

    def _should_retry(self, attempt: int) -> bool:
        return attempt < self.retries - 1

    def _wait_before_retry(self, attempt: int, reason: str) -> None:
        if not self._should_retry(attempt):
            raise Exception(f'Превышено количество попыток. Причина: {reason}')
        wait_time = min(2 ** attempt, MAX_WAIT_SECONDS)
        logger.info(f'Повтор через {wait_time} сек. (причина: {reason})')
        time.sleep(wait_time)


class MedClient(Client):
    def __init__(self, base_urls: dict[MedUrlKey, str] = MED_BASE_URLS):
        self.base_urls = base_urls

    def make_request(self, url_key: MedUrlKey) -> requests.Response:
        url = self.base_urls[url_key]
        logger.info(f'Запрос Med коллекции: {url_key}')
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response