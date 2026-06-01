from dataclasses import asdict, dataclass, field

import pandas as pd

from ozon.utils.date_helpers import get_month_ago_iso, get_last_sunday_end_iso


@dataclass
class OrdersDTO:
    filter: dict = field(default_factory=lambda: {
        "processed_at_from": get_month_ago_iso(),
        "processed_at_to": get_last_sunday_end_iso(),
        # "processed_at_from": '2026-04-27T00:00:00+00:00',
        # "processed_at_to": '2026-05-03T23:59:59+00:00',
        "sku": [],
        "cancel_reason_id": [],
        "offer_id": "",
        "status_alias": [],
        "statuses": [],
        "title": ""
    })


