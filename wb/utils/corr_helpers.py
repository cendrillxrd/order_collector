from typing import Literal

import pandas as pd

from wb.wb_config import BASE_COLUMNS_SALES_NAME, BASE_COLUMNS_ORDERS_NAME


def correct_columns_name(df: pd.DataFrame, base_columns_name: dict) -> pd.DataFrame:
    columns_rename = {k: v for k, v in base_columns_name.items() if k in df.columns}
    return df.rename(columns=columns_rename)