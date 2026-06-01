from dataclasses import field, dataclass

from ozon.config import LIMIT_RETURNS
from ozon.utils.date_helpers import get_month_ago_iso, get_last_sunday_end_iso, date_month_ago, end_of_last_week


@dataclass
class ReturnedDTO:
    filter: dict = field(default_factory=lambda: {
        "logistic_return_date": {
                # "time_from": "2026-04-27T00:00:00Z",
                # "time_to": "2026-05-03T23:59:59Z"
                "time_from": date_month_ago(),
                "time_to": end_of_last_week()
            },
    })
    limit: int = LIMIT_RETURNS