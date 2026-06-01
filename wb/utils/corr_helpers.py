from typing import Literal

import pandas as pd

from wb.config import BASE_COLUMNS_SALES_NAME, BASE_COLUMNS_ORDERS_NAME


def correct_columns_name(df: pd.DataFrame, table_name: Literal['orders', 'sales']) -> pd.DataFrame:
    if table_name == 'orders':
        base_columns_name = BASE_COLUMNS_ORDERS_NAME
    elif table_name == 'sales':
        base_columns_name = BASE_COLUMNS_SALES_NAME
    else:
        raise ValueError('table_name must be one of orders, sales')
    columns_name = [column for column in df.columns if column in base_columns_name]

    columns_rename = {k: base_columns_name.get(k) for k in columns_name}
    df.rename(columns_rename,
              inplace=True,
              axis=1)
    return df