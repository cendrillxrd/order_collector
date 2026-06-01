import time
from typing import Literal, Optional, Dict
from wb.config import BASE_URLS, API_KEYS
import requests

from wb.strategies.request_strategies import RequestStrategy


class WildberriesAPIClient():
    def __init__(self,):
        self.base_url = BASE_URLS
        self.api_key = API_KEYS
        self.session = requests.Session()
        self.__strategy = None

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def make_request(self, method: Literal['GET', 'POST'],
                     api_type: Literal['Analytics_Statistics_API_KEY', 'Price_discount_API_KEY'],
                     url_key: Literal['seller-analytics', 'discounts-prices', 'dp-calendar'],
                     endpoint: str,
                     params: Optional[Dict] = None,
                     payload: Optional[Dict] = None,
                     zip_needs: bool = False,
                     retries: int = 5):
        url = f'{self.base_url[url_key]}{endpoint}'

        if zip_needs:
            self.session.headers.update({'Content-Type': 'application/zip'})
        else:
            self.session.headers.update({'Content-Type': 'application/json'})

        for attempt in range(retries):
            try:
                self.session.headers.update({'Authorization': self.api_key[api_type]})
                response = self.session.request(method=method, url=url, params=params, json=payload, timeout=30)

                response.raise_for_status()

                # Обработка ответа
                if zip_needs:
                    return response
                else:
                    return self._safe_json_parse(response, attempt, retries)

            except requests.exceptions.JSONDecodeError as json_err:
                if self._should_retry(attempt, retries):
                    self._wait_before_retry(attempt, "JSON ошибка")
                    continue
                raise

            except requests.exceptions.HTTPError as err:
                if self._should_retry(attempt, retries) and self._is_retryable_http_error(err):
                    self._wait_before_retry(attempt, f"HTTP ошибка {err.response.status_code}")
                    continue
                raise

            except requests.exceptions.RequestException as err:
                if self._should_retry(attempt, retries):
                    self._wait_before_retry(attempt, "ошибка соединения")
                    continue
                raise

        return None

    def _safe_json_parse(self, response, attempt, retries):
        """Безопасный парсинг JSON с повторными попытками"""
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as json_err:

            if self._should_retry(attempt, retries):
                self._wait_before_retry(attempt, "JSON парсинг")
                raise json_err
            else:
                raise requests.exceptions.JSONDecodeError(
                    f"JSON парсинг не удался после {retries} попыток",
                    response.text, 0
                )

    @staticmethod
    def _should_retry(attempt, retries):
        """Определяет, нужно ли повторять запрос"""
        return attempt < retries - 1

    @staticmethod
    def _is_retryable_http_error(err):
        """Определяет, является ли HTTP ошибка повторяемой"""
        if err.response:
            return err.response.status_code in (429, 500, 502, 503, 504)
        return False

    @staticmethod
    def _wait_before_retry(attempt, reason):
        """Ожидание перед повторной попыткой"""
        wait_time = min(2 ** attempt, 10)
        time.sleep(wait_time)

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self, **kwargs)
