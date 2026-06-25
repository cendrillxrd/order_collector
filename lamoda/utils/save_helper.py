import os
from pathlib import Path

import pandas as pd

from lamoda.lamoda_config import (BASE_COLUMNS_NAME, FILE_PATH, NOMENCLATURE_DAY_FILE_NAME,
                                  ORDERS_FILE_NAME)


def save_info(info):
    """Сохраняет таблицы в csv файл."""
    for key, value in info.items():
        file_name = f'{FILE_PATH}/{key}.csv'
        if key == NOMENCLATURE_DAY_FILE_NAME:
            value.to_csv(file_name, index=False, encoding='cp1251')
        elif key == ORDERS_FILE_NAME:
            value.to_csv(file_name, index=False, encoding='cp1251')
        else:
            if is_csv_empty(file_name):
                value.to_csv(file_name, index=False, encoding='cp1251')
            else:
                value.to_csv(file_name, mode='a', index=False, encoding='cp1251', header=False)


def is_csv_empty(file_path: str) -> bool:
    """Проверяет, пустой ли файл."""
    if not os.path.exists(file_path):
        return True
    file_extension = Path(file_path).suffix.lower()
    if file_extension != '.csv':
        return True
    df = pd.read_csv(file_path, encoding='cp1251')
    return df.empty


def correct_columns_name(df: pd.DataFrame) -> pd.DataFrame:
    columns_name = [column for column in df.columns if column in BASE_COLUMNS_NAME]

    columns_rename = {k: BASE_COLUMNS_NAME.get(k) for k in columns_name}
    df.rename(columns_rename,
              inplace=True,
              axis=1)
    return df
