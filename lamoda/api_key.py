import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv, set_key
from typing import Literal

from lamoda.workers.api_client import APIClient


class ApiKeyManager:
    """
    Менеджер API ключей с использованием environment variables
    для хранения состояния между запусками приложения.
    """

    def __init__(self, market_type: str = Literal['ufo', 'smart_premium'], env_file: str = ".env"):
        self.market_type = market_type
        if market_type == 'ufo':
            self.api_key_name = 'API_KEY'
        elif market_type == 'smart_premium':
            self.api_key_name = 'API_KEY_SMART_PREMIUM'
        else:
            raise ValueError("market_type must be 'ufo' or 'smart_premium'")
        self.api_key_name = self.api_key_name
        self.created_at_name = f"{self.api_key_name}_CREATED_AT"
        self.env_file = env_file
        self.key: Optional[str] = None
        self.created_at: Optional[datetime] = None
        # Время жизни ключа в минутах
        self.key_lifetime_minutes: int = 15

        # Создаем .env файл если его нет
        if not os.path.exists(self.env_file):
            open(self.env_file, 'w').close()

        # Загружаем переменные
        load_dotenv(self.env_file)

        self._initialize_key()

    def _initialize_key(self) -> None:
        """Инициализирует или обновляет API ключ"""
        if self._should_renew():
            self._renew_key()
        else:
            self._load_existing_key()

    def _should_renew(self) -> bool:
        """
        Проверяет, нужно ли обновлять ключ.
        Возвращает True если:
        - Ключ отсутствует в environment variables
        - Ключ просрочен (больше 15 минут)
        """
        existing_key = os.getenv(self.api_key_name)
        created_at_str = os.getenv(self.created_at_name)

        # Если нет ключа или даты создания
        if not existing_key or not created_at_str:
            return True

        try:
            created_at = datetime.fromisoformat(created_at_str)
            # Проверяем, прошло ли более 15 минут
            return datetime.now() - created_at > timedelta(minutes=self.key_lifetime_minutes)
        except (ValueError, TypeError):
            # Если дата в неправильном формате
            return True

    def _load_existing_key(self) -> None:
        self.key = os.getenv(self.api_key_name)
        created_at_str = os.getenv(self.created_at_name)

        if not created_at_str:
            # Нет даты → ключ невалиден
            self.key = None
            return

        try:
            self.created_at = datetime.fromisoformat(created_at_str)
        except ValueError:
            # Неверный формат даты → ключ невалиден
            self.key = None
            self.created_at = None

    def _renew_key(self) -> None:
        """
        Получает новый API ключ и сохраняет его в environment variables.
        В реальном приложении здесь будет вызов вашего API.
        """
        # Получаем новый ключ (заглушка для реального API)
        self.key = self._get_new_key_from_api()
        self.created_at = datetime.now()

        # Сохраняем в environment variables
        self._save_to_environment()

        print(f"Новый API ключ создан")
        print(f"Время создания: {self.created_at}")
        print(f"Ключ будет действителен {self.key_lifetime_minutes} минут")

    def _get_new_key_from_api(self) -> str:
        """
        Метод для получения нового ключа из API.
        Здесь должна быть ваша реальная логика.
        """
        try:
            api_client = APIClient()
            api_key = api_client.get_new_api_key(self.market_type)
            return api_key
        except Exception as e:
            raise Exception(f"Ошибка при получении API ключа: {e}")

    def _save_to_environment(self) -> None:
        """Сохраняет ключ и дату в environment variables"""
        set_key(self.env_file, self.api_key_name, self.key)
        set_key(self.env_file, self.created_at_name, self.created_at.isoformat())

        # Обновляем текущее окружение
        load_dotenv(self.env_file, override=True)

    def get_key(self) -> str:
        """Возвращает текущий API ключ"""
        if not self.key:
            raise ValueError("API ключ не инициализирован")
        return self.key

    def get_key_info(self) -> dict:
        """Возвращает информацию о текущем ключе"""
        return {
            "key": self.key,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_in": self._get_expiration_info(),
            "lifetime_minutes": self.key_lifetime_minutes
        }

    def _get_expiration_info(self) -> Optional[str]:
        """Возвращает информацию о времени до истечения ключа"""
        if not self.created_at:
            return None

        expiration_time = self.created_at + timedelta(minutes=self.key_lifetime_minutes)
        time_left = expiration_time - datetime.now()

        if time_left.total_seconds() <= 0:
            return "Истек"

        # Для 15 минут удобнее показывать в минутах и секундах
        minutes = int(time_left.total_seconds() // 60)
        seconds = int(time_left.total_seconds() % 60)

        if minutes > 0:
            return f"{minutes}м {seconds}с"
        else:
            return f"{seconds}с"

    def force_renew(self) -> None:
        """Принудительное обновление ключа"""
        print("Принудительное обновление ключа...")
        self._renew_key()