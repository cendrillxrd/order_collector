import time
from abc import ABC, abstractmethod
from typing import Literal, Union

import requests

from yandex.config import API_KEY_YANDEX, BASE_URLS
from yandex.strategies.requests_strategies import RequestStrategy


class Client(ABC):
    @abstractmethod
    def make_request(self, **kwargs):
        pass

    @abstractmethod
    def get_data(self):
        pass

class YandexAPIClient(Client):
    def __init__(self):
        self.base_url = BASE_URLS['yandex']
        self.session = requests.Session()
        self.session.headers.update({
            'Api-Key': API_KEY_YANDEX,
            'Content-Type': 'application/json'
        })
        self.__strategy = None

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def make_request(self,
                     method: Literal['GET', 'POST'],
                     endpoint,
                     params=None,
                     json=None,
                     retries=5):
        url = f'{self.base_url}{endpoint}'

        for attempt in range(retries):
            try:
                response = self.session.request(method, url, params=params, json=json, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.HTTPError as err:
                if err.response.status_code < 500 and err.response.status_code != 429:
                    raise
                if attempt == retries - 1:
                    raise
            except (requests.ConnectionError, requests.Timeout):
                if attempt == retries - 1:
                    raise

            time.sleep(min(2 ** attempt, 30))

        return None

    def get_data(self, **kwargs) -> Union[list[dict], int, str, dict[str, dict]]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self, **kwargs)

class MedClient(Client):
    def __init__(self):
        self.base_url = BASE_URLS
        self.__strategy = None

    def make_request(self, url_key: Literal['med_collections_1', 'med_collections_2'], login: str = None,
                     password: str = None,):
        url = f'{self.base_url[url_key]}'
        response = requests.get(url, auth=(login, password))
        return response

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self, **kwargs)

class HttpClient(Client):
    def __init__(self):
        self.__strategy = None

    def make_request(self, url: str):
        response = requests.get(url)
        return response

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self, **kwargs)