import time
from typing import Dict, Literal, Optional
from urllib3.util.retry import Retry
import requests
import urllib3
from requests.adapters import HTTPAdapter
from lamoda.config import BASE_URLS, CLIENT_ID, CLIENT_SECRET, CLIENT_ID_SMART_PREMIUM, CLIENT_SECRET_SMART_PREMIUM
from lamoda.strategies.request_strategies import RequestStrategy


class APIClient:
    def __init__(self, api_key_manager: "ApiKeyManager" = None):
        self.base_url = BASE_URLS
        self.api_key_manager = api_key_manager
        if api_key_manager is not None:
            try:
                self.api_key = api_key_manager.get_key()
            except Exception as e:
                print(f"Ошибка получения ключа API: {e}")
                self.api_key = None
        else:
            self.api_key = None

        # Создаем сессию с адаптером для повторных попыток
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({'Content-Type': 'application/json'})
        self.__strategy = None

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def _update_auth_header(self):
        """Обновляет заголовок Authorization с текущим API ключом"""
        if self.api_key:
            self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
        else:
            # Удаляем заголовок, если ключа нет
            self.session.headers.pop('Authorization', None)

    def make_request(
            self,
            url_key: Literal['live', 'b2b'],
            method: Literal['GET', 'POST'],
            endpoint: str,
            params: Optional[Dict] = None,
            payload: Optional[Dict] = None,
            retries: int = 5):

        url = f'{self.base_url[url_key]}{endpoint}'

        for attempt in range(retries):
            try:
                self._update_auth_header()

                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=payload,
                    timeout=(30, 30)  # Уменьшил таймаут до 30 секунд
                )

                # Проверяем статус код
                if response.status_code == 401:
                    if self.api_key_manager:
                        try:
                            self.api_key_manager.force_renew()
                            self.api_key = self.api_key_manager.get_key()
                            self._update_auth_header()
                            print(f"Обновлен API ключ, повтор через 10 секунд...")
                            time.sleep(10)
                            continue
                        except Exception as e:
                            print(f"Ошибка при обновлении ключа: {e}")
                            if attempt == retries - 1:
                                raise
                            time.sleep(10)
                            continue
                    else:
                        print("Нет менеджера ключей для обновления")
                        if attempt == retries - 1:
                            raise Exception("401 Unauthorized и нет менеджера ключей")
                        time.sleep(10)
                        continue

                # Проверяем другие статус коды для повторных попыток
                if response.status_code in (429, 500, 502, 503, 504, 443):
                    print(f'Retrying... (попытка {attempt + 1}/{retries})')
                    wait_time = min(2 ** attempt, 10)
                    time.sleep(wait_time)
                    continue

                # Проверяем успешный статус код
                response.raise_for_status()

                # Обработка zip файлов
                if 'application/zip' in response.headers.get('Content-Type', ''):
                    return response

                # Парсим JSON
                try:
                    response_json = response.json()
                except requests.exceptions.JSONDecodeError:
                    print(f"Ошибка декодирования JSON. Ответ: {response.text[:200]}")
                    if attempt == retries - 1:
                        raise Exception("Не удалось декодировать JSON ответ")
                    time.sleep(2 ** attempt)
                    continue

                # Проверяем наличие ошибки в ответе
                if isinstance(response_json, dict) and response_json.get('error'):
                    print(f"Ошибка в ответе API: {response_json.get('error')}")
                    if (response_json.get('error') == 'invalid_token') or (response_json.get('error') == {'code': 50401, 'message': 'invalid_grant', 'data': {'errors': []}}):
                        if self.api_key_manager:
                            try:
                                self.api_key_manager.force_renew()
                                self.api_key = self.api_key_manager.get_key()
                                self._update_auth_header()
                                time.sleep(10)
                                continue
                            except Exception:
                                pass
                    if attempt == retries - 1:
                        raise Exception(f"API вернул ошибку: {response_json.get('error')}")
                    time.sleep(10)
                    continue

                return response_json

            except requests.exceptions.ReadTimeout as err:
                print(f"Таймаут чтения (попытка {attempt + 1}/{retries}): {err}")
                if attempt < retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    print(f"Повтор через {wait_time} секунд...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Превышено количество попыток. Последняя ошибка: Таймаут чтения")

            except requests.exceptions.ConnectTimeout as err:
                print(f"Таймаут подключения (попытка {attempt + 1}/{retries}): {err}")
                if attempt < retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Превышено количество попыток. Последняя ошибка: Таймаут подключения")

            except requests.exceptions.ConnectionError as err:
                print(f"Ошибка соединения (попытка {attempt + 1}/{retries}): {err}")
                if attempt < retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Превышено количество попыток. Последняя ошибка: Ошибка соединения")

            except requests.exceptions.SSLError as err:
                print(f"SSL ошибка (попытка {attempt + 1}/{retries}): {err}")
                if attempt < retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Превышено количество попыток. Последняя ошибка: SSL ошибка")

            except requests.exceptions.HTTPError as err:
                print(f"HTTP ошибка (попытка {attempt + 1}/{retries}): {err}")
                if attempt < retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Превышено количество попыток. Последняя ошибка: {err}")

            except requests.exceptions.RequestException as err:
                print(f"Ошибка запроса (попытка {attempt + 1}/{retries}): {err}")
                if attempt == retries - 1:
                    raise Exception(f"Превышено количество попыток. Последняя ошибка: {err}")
                time.sleep(2 ** attempt)

            except urllib3.exceptions.ProtocolError as e:
                print(f"Ошибка протокола (попытка {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    print(f"Повтор через {wait_time} секунд...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Превышено количество попыток. Последняя ошибка: {e}")

            except Exception as e:
                print(f"Неожиданная ошибка (попытка {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    raise Exception(f"Неожиданная ошибка после {retries} попыток: {e}")
                time.sleep(2 ** attempt)

        return None

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        try:
            return self.__strategy.get_info(self, **kwargs)
        except Exception as e:
            print(f"Ошибка при получении данных через стратегию: {e}")
            raise

    def get_new_api_key(self, market_type: str = 'ufo'):
        endpoint = '/auth/token'
        try:
            if market_type == 'ufo':
                params = {
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'grant_type': 'client_credentials',
                }
            elif market_type == 'smart_premium':
                params = {
                    'client_id': CLIENT_ID_SMART_PREMIUM,
                    'client_secret': CLIENT_SECRET_SMART_PREMIUM,
                    'grant_type': 'client_credentials',
                }
            else:
                raise ValueError('market_type must be ufo or smart_premium')

            response = self.make_request(method='GET',
                                         url_key='live',
                                         params=params,
                                         endpoint=endpoint,
                                         retries=3)

            if response and 'access_token' in response:
                return response['access_token']
            else:
                raise Exception("Не удалось получить access_token из ответа")

        except Exception as e:
            print(f"Ошибка при получении нового API ключа: {e}")
            raise


class MedClient:
    def __init__(self):
        self.base_url = BASE_URLS
        self.__strategy = None

    def make_request(self, url_key: Literal['med_collections_1', 'med_collections_2'], login: str = None,
                     password: str = None, ):
        url = f'{self.base_url[url_key]}'
        response = requests.get(url, auth=(login, password))
        return response

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self, **kwargs)
