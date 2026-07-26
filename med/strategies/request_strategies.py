from abc import ABC, abstractmethod

import requests

from logger import setup_logger
from med.med_config import MedUrlKey
from med.dto.request_med_config import RequestMedConfig
from med.workers.client import Client, MedClient

logger = setup_logger("my_app")

class RequestStrategy(ABC):
    @abstractmethod
    def do_request(self, client: Client, **kwargs) -> list[dict]:
        pass

class ReqMEDCollections(RequestStrategy):
    def __init__(self, url_key: MedUrlKey):
        self.url_key = url_key

    def do_request(self, client: MedClient, **kwargs) -> requests.Response:
        config = RequestMedConfig(
            url_key=self.url_key
        )
        return client.make_request(config)