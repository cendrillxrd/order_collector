from dataclasses import asdict, dataclass
from typing import Optional

import pandas as pd


@dataclass
class InfoDTO:
    orders: Optional[pd.DataFrame] = None
    cards_info: Optional[pd.DataFrame] = None
    returns: Optional[pd.DataFrame] = None
    all_orders: Optional[pd.DataFrame] = None
    all_returns: Optional[pd.DataFrame] = None