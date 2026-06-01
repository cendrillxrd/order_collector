from dataclasses import asdict, dataclass

import pandas as pd


@dataclass
class InfoUpdateDTO:
    orders: pd.DataFrame
