from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, Any

from lamoda.lamoda_config import LamodaUrlKey

@dataclass
class RequestLamodaConfig:
    method: Literal['GET', 'POST']
    url_key: LamodaUrlKey
    endpoint: str
    params: Optional[Dict[str, Any]] = field(default=None)
    payload: Optional[Dict[str, Any]] = field(default=None)