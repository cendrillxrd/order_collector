from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, Any
from lamoda.lamoda_config import ApiType, WBUrlKey

@dataclass
class RequestLamodaConfig:
    method: Literal['GET', 'POST']
    api_type: ApiType
    url_key: WBUrlKey
    endpoint: str
    params: Optional[Dict[str, Any]] = field(default=None)
    payload: Optional[Dict[str, Any]] = field(default=None)
    zip_needs: bool = False