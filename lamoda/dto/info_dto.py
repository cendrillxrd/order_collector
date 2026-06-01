from dataclasses import asdict, dataclass
from typing import Optional

import pandas as pd


@dataclass
class InfoDTO:
    all_orders: Optional[pd.DataFrame] = None
    nomenclature: Optional[pd.DataFrame] = None
    orders_month: Optional[pd.DataFrame] = None
    collection1: Optional[pd.DataFrame] = None
    collection2: Optional[pd.DataFrame] = None
    collection3: Optional[pd.DataFrame] = None
    collection4: Optional[pd.DataFrame] = None
