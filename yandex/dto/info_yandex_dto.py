from dataclasses import asdict, dataclass
from typing import Optional

import pandas as pd


@dataclass
class InfoYandexDTO:
    orders: Optional[pd.DataFrame] = None
    returns: Optional[pd.DataFrame] = None
    all_orders: Optional[pd.DataFrame] = None
    all_returns: Optional[pd.DataFrame] = None
    med_collection_1: Optional[pd.DataFrame] = None
    med_collection_2: Optional[pd.DataFrame] = None
    med_collection_3: Optional[pd.DataFrame] = None
    med_collection_4: Optional[pd.DataFrame] = None