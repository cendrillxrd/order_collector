import os
import requests
from datetime import datetime, timedelta
from typing import Optional, Literal

from dotenv import load_dotenv, set_key

from lamoda.lamoda_config import (
    CLIENT_ID, CLIENT_SECRET,
    CLIENT_ID_SMART_PREMIUM, CLIENT_SECRET_SMART_PREMIUM,
    LamodaUrlKey, BASE_URLS,
)


class ApiKeyManager:
    """
    Менеджер API ключей с хранением состояния в environment variables.
    Получает токен напрямую через requests — без зависимости от APIClient.
    """

    KEY_LIFETIME_MINUTES = 15
    TOKEN_ENDPOINT = '/auth/token'

    def __init__(
        self,
        market_type: type[str] = Literal['ufo', 'smart_premium'],
        env_file: str = '.env',
    ):
        self.market_type = market_type
        self.env_file = env_file

        if market_type == 'ufo':
            self.api_key_name = 'API_KEY'
        elif market_type == 'smart_premium':
            self.api_key_name = 'API_KEY_SMART_PREMIUM'
        else:
            raise ValueError("market_type must be 'ufo' or 'smart_premium'")

        self.created_at_name = f'{self.api_key_name}_CREATED_AT'
        self.key: Optional[str] = None
        self.created_at: Optional[datetime] = None

        if not os.path.exists(self.env_file):
            open(self.env_file, 'w').close()

        load_dotenv(self.env_file)
        self._initialize_key()

    def _initialize_key(self) -> None:
        if self._should_renew():
            self._renew_key()
        else:
            self._load_existing_key()

    def _should_renew(self) -> bool:
        existing_key = os.getenv(self.api_key_name)
        created_at_str = os.getenv(self.created_at_name)
        if not existing_key or not created_at_str:
            return True
        try:
            created_at = datetime.fromisoformat(created_at_str)
            return datetime.now() - created_at > timedelta(minutes=self.KEY_LIFETIME_MINUTES)
        except (ValueError, TypeError):
            return True

    def _load_existing_key(self) -> None:
        self.key = os.getenv(self.api_key_name)
        created_at_str = os.getenv(self.created_at_name)
        if not created_at_str:
            self.key = None
            return
        try:
            self.created_at = datetime.fromisoformat(created_at_str)
        except ValueError:
            self.key = None
            self.created_at = None

    def _renew_key(self) -> None:
        self.key = self._fetch_token_from_api()
        self.created_at = datetime.now()
        self._save_to_environment()

    def _fetch_token_from_api(self) -> str:
        """Получает токен напрямую через requests — без зависимости от APIClient."""
        if self.market_type == 'ufo':
            params = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'grant_type': 'client_credentials',
            }
        else:
            params = {
                'client_id': CLIENT_ID_SMART_PREMIUM,
                'client_secret': CLIENT_SECRET_SMART_PREMIUM,
                'grant_type': 'client_credentials',
            }

        url = f'{BASE_URLS[LamodaUrlKey.LIVE]}{self.TOKEN_ENDPOINT}'
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if 'access_token' not in data:
            raise Exception(f'access_token отсутствует в ответе: {data}')
        return data['access_token']

    def _save_to_environment(self) -> None:
        set_key(self.env_file, self.api_key_name, self.key)
        set_key(self.env_file, self.created_at_name, self.created_at.isoformat())
        load_dotenv(self.env_file, override=True)

    def get_key(self) -> str:
        if not self.key:
            raise ValueError('API ключ не инициализирован')
        return self.key

    def force_renew(self) -> None:
        self._renew_key()