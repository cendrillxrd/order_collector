from dataclasses import asdict, dataclass, field
from typing import Optional

import pandas as pd


@dataclass
class InfoYandexDTO:
    orders: Optional[pd.DataFrame] = None
    returns: Optional[pd.DataFrame] = None
    all_orders: Optional[pd.DataFrame] = None
    all_returns: Optional[pd.DataFrame] = None
    med_collections: list[pd.DataFrame] = field(default_factory=list)