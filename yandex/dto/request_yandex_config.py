from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, Any

from yandex.yandex_config import YandexUrlKey, MedUrlKey


@dataclass
class RequestYandexConfig:
    method: Literal['GET', 'POST']
    url_key: YandexUrlKey | MedUrlKey
    endpoint: str
    params: Optional[Dict[str, Any]] = field(default_factory=dict)
    payload: Optional[Dict[str, Any]] = field(default_factory=dict)