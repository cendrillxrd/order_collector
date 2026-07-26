from abc import ABC, abstractmethod

import requests

from logger import setup_logger
from med.med_config import MED_BASE_URLS
from med.dto.request_med_config import RequestMedConfig

logger = setup_logger("my_app")

class Client(ABC):
    @abstractmethod
    def make_request(self, config: RequestMedConfig):
        pass

class MedClient(Client):
    def __init__(self, base_urls: dict = MED_BASE_URLS):
        self.base_urls = base_urls

    def make_request(self, config: RequestMedConfig) -> requests.Response:
        url = self.base_urls[config.url_key]
        response = requests.get(url)
        response.raise_for_status()
        return response