from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Literal

from lamoda.config import LIMIT_ORDER
from lamoda.utils.date_helper import (get_date_range_filter, parse_date_string)


@dataclass
class OrderDTO:
    limit: int = LIMIT_ORDER
    page: int = 1
    sort: str = 'createdAt'
    filter: str = field(init=False)

    def __post_init__(self):
        # По умолчанию без фильтра
        self.filter = None

    @classmethod
    def with_date_range(cls, start_date: str, end_date: str, **kwargs):
        """Альтернативный конструктор с диапазоном дат"""
        instance = cls(**kwargs)
        instance.filter = get_date_range_filter(parse_date_string(start_date, True), parse_date_string(end_date, False))
        return instance
