from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, Any
from wb.wb_config import ApiType, UrlKey

@dataclass
class RequestConfig:
    method: Literal['GET', 'POST']
    api_type: ApiType
    url_key: UrlKey
    endpoint: str
    params: Optional[Dict[str, Any]] = field(default=None)
    payload: Optional[Dict[str, Any]] = field(default=None)
    zip_needs: bool = False