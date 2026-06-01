import random
from abc import ABC, abstractmethod
from ozon.config import API_KEY, BASE_URLS, CLIENT_ID
from ozon.strategies.request_strategies import RequestStrategy
import time
import requests
from typing import Dict, Optional, Literal
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OzonAPIClient():
    def __init__(self):
        self.base_url = BASE_URLS
        self.api_key = API_KEY
        self.client_id = CLIENT_ID
        self.session = requests.Session()
        self.__strategy = None
        self._setup_session()

    def _setup_session(self):
        """Настройка сессии с повторными попытками на уровне соединения"""
        retry_strategy = Retry(
            total=3,  # дополнительные попытки на уровне соединения
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"],
            # Обрабатываем ошибки соединения
            raise_on_status=False
        )

        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Базовые заголовки
        self.session.headers.update({
            'Client-Id': self.client_id,
            'Api-Key': self.api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def make_request(self, method: Literal['GET', 'POST'],
                     url_key: Literal['seller-analytics', 'discounts-prices', 'dp-calendar'],
                     endpoint: str,
                     params: Optional[Dict] = None,
                     payload: Optional[Dict] = None,
                     zip_needs: bool = False,
                     retries: int = 5):
        url = f'{self.base_url[url_key]}{endpoint}'

        # Устанавливаем Content-Type
        if zip_needs:
            content_type = 'application/zip'
        else:
            content_type = 'application/json'

        headers = self.session.headers.copy()
        headers['Content-Type'] = content_type

        for attempt in range(retries):
            try:
                # log_message('app', f'Попытка {attempt + 1}/{retries} для {url}', 'INFO')

                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=payload,
                    headers=headers,
                    timeout=(30, 60)  # (connect_timeout, read_timeout)
                )
                response.raise_for_status()
                # log_message('app', 'Запрос выполнен успешно', 'INFO')

                if content_type == 'application/zip':
                    return response
                return response.json()

            except requests.exceptions.HTTPError as err:
                error_status = err.response.status_code if err.response else 'unknown'
                # log_message('app', f'HTTP ошибка {error_status}: {err}', 'ERROR')

                # Для ошибок сервера делаем повторные попытки
                if err.response and err.response.status_code in (429, 500, 502, 503, 504):
                    wait_time = min(2 ** attempt + random.uniform(0.1, 0.5), 30)
                    # log_message('app', f"Повтор через {wait_time:.1f} секунд...", 'INFO')
                    time.sleep(wait_time)
                    continue

                # Для клиентских ошибок не повторяем
                raise

            except requests.exceptions.ConnectionError as err:
                # log_message('app', f'Ошибка соединения (попытка {attempt + 1}/{retries}): {err}', 'ERROR')

                if attempt < retries - 1:
                    wait_time = min(2 ** attempt + random.uniform(0.5, 1.5), 30)
                    # log_message('app', f"Повтор через {wait_time:.1f} секунд...", 'INFO')
                    time.sleep(wait_time)
                    continue
                else:
                    # log_message('app', 'Все попытки соединения провалились', 'ERROR')
                    raise

            except requests.exceptions.Timeout as err:
                # log_message('app', f'Таймаут (попытка {attempt + 1}/{retries}): {err}', 'ERROR')

                if attempt < retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    # log_message('app', f"Повтор через {wait_time} секунд...", 'INFO')
                    time.sleep(wait_time)
                    continue
                raise

            except requests.exceptions.RequestException as err:
                # log_message('app', f'Ошибка запроса (попытка {attempt + 1}/{retries}): {err}', 'ERROR')

                if attempt < retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    # log_message('app', f"Повтор через {wait_time} секунд...", 'INFO')
                    time.sleep(wait_time)
                    continue
                raise

        return None

    def get_data(self, **kwargs):
        """Основной метод для получения данных через стратегию"""
        if not self.__strategy:
            raise ValueError("Strategy not set")
        return self.__strategy.get_info(self, **kwargs)

class HttpClient():
    def __init__(self):
        self.__strategy = None

    def make_request(self, url):
        # log_message('app', f'Выполнение запроса по адресу {url}', 'INFO')
        response = requests.get(url, timeout=(120, 120))
        return response

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self, **kwargs)

class MedClient():
    def __init__(self):
        self.base_url = BASE_URLS
        self.__strategy = None

    def make_request(self, url_key: Literal['med_prices', 'med_collections_1', 'med_collections_2']):
        url = f'{self.base_url[url_key]}'
        # log_message('app', f'Выполнение запроса по адресу {url}', 'INFO')
        response = requests.get(url, timeout=30)
        return response

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self)