
from dataclasses import asdict, dataclass
from typing import Optional

import pandas as pd


@dataclass
class InfoDTO:
    orders: Optional[pd.DataFrame] = None
    sales: Optional[pd.DataFrame] = None
    all_orders: Optional[pd.DataFrame] = None
    all_sales: Optional[pd.DataFrame] = None

