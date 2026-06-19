from dataclasses import dataclass
from ozon.ozon_config import OZONUrlKey

@dataclass
class RequestHTTPConfig:
    url_key: OZONUrlKey
    endpoint: str