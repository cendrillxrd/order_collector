import pandas as pd


def correct_columns_name(df: pd.DataFrame, base_columns_name: dict) -> pd.DataFrame:
    columns_rename = {k: v for k, v in base_columns_name.items() if k in df.columns}
    return df.rename(columns=columns_rename)