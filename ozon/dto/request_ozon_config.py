from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, Any
from ozon.ozon_config import OZONUrlKey

@dataclass
class RequestOZONConfig:
    method: Literal['GET', 'POST']
    url_key: OZONUrlKey
    endpoint: str
    params: Optional[Dict[str, Any]] = field(default=None)
    payload: Optional[Dict[str, Any]] = field(default=None)
    zip_needs: bool = False