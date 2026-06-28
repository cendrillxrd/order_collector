import pandas as pd
from sqlalchemy import text
import numpy as np
from db import engine
from logger import setup_logger

logger = setup_logger("my_app")

ID_LIKE_COLUMNS = {'sku', 'return_id', 'posting_number', 'order_number'}

OZON_ORDERS_COLUMN_MAP = {
    'Номер отправления': 'posting_number',
    'Номер заказа': 'order_number',
    'Принят в обработку': 'created_at',
    'Статус': 'status',
    'Дата доставки': 'post_date',
    'Дата отмены': 'canceled_date',
    'Сумма отправления': 'price',
    'Бренд': 'brand',
    'Название товара': 'name',
    'Цвет товара': 'color',
    'Название предмета': 'size',
    'SKU': 'sku',
    'Артикул': 'offer_id',
    'Количество': 'quantity',
    'Цена товара до скидок': 'price_without_discount',
    'Скидка %': 'discount',
}

OZON_RETURNS_COLUMN_MAP = {
    'ID возврата': 'return_id',
    'Номер заказа': 'order_number',
    'Номер отправления': 'posting_number',
    'Дата возврата': 'return_date',
    'Тип возврата': 'return_type',
    'Причина возврата': 'return_reason_name',
    'Схема возврата': 'return_schema',
    'SKU': 'sku',
    'Артикул': 'offer_id',
    'Название товара': 'name',
    'Сумма отправления': 'price',
    'Количество': 'quantity',
    'Бренд': 'brand',
}

def upsert_ozon_orders(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        logger.info("Нет новых заказов Ozon для записи в БД")
        return

    df = df.rename(columns=OZON_ORDERS_COLUMN_MAP)
    df = df[[c for c in OZON_ORDERS_COLUMN_MAP.values() if c in df.columns]]

    # считаем позицию — аналог _temp_position из MergeOrdersInfoStrategy
    df = df.copy()
    df['position'] = df.groupby(['posting_number', 'offer_id']).cumcount()

    records = _clean_records(df)

    columns = list(df.columns)
    placeholders = ', '.join(f':{c}' for c in columns)
    update_clause = ', '.join(
        f'{c} = VALUES({c})'
        for c in columns
        if c not in ('posting_number', 'offer_id', 'position')
    )

    query = text(f"""
        INSERT INTO ozon_orders ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """)

    with engine.begin() as conn:
        conn.execute(query, records)

    logger.info(f"Ozon orders: записано/обновлено {len(records)} строк в БД")

def upsert_ozon_returns(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        logger.info("Нет новых возвратов Ozon для записи в БД")
        return

    df = df.rename(columns=OZON_RETURNS_COLUMN_MAP)
    df = df[[c for c in OZON_RETURNS_COLUMN_MAP.values() if c in df.columns]]
    df = df.copy()
    df['position'] = df.groupby(['return_id', 'offer_id']).cumcount()
    records = _clean_records(df)

    columns = list(df.columns)
    placeholders = ', '.join(f':{c}' for c in columns)
    update_clause = ', '.join(
        f'{c} = VALUES({c})'
        for c in columns
        if c not in ('return_id', 'offer_id', 'position')
    )

    query = text(f"""
        INSERT INTO ozon_returns ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """)

    with engine.begin() as conn:
        conn.execute(query, records)

    logger.info(f"Ozon returns: записано/обновлено {len(records)} строк в БД")

OZON_ORDERS_COLUMN_MAP_INV  = {v: k for k, v in OZON_ORDERS_COLUMN_MAP.items()}
OZON_RETURNS_COLUMN_MAP_INV = {v: k for k, v in OZON_RETURNS_COLUMN_MAP.items()}

def read_ozon_orders() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM ozon_orders"), conn)
    df = df.rename(columns=OZON_ORDERS_COLUMN_MAP_INV)
    df = df[[c for c in OZON_ORDERS_COLUMN_MAP_INV.values() if c in df.columns]]
    logger.info(f"Ozon orders: прочитано {len(df)} строк из БД")
    return df

def read_ozon_returns() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM ozon_returns"), conn)
    df = df.rename(columns=OZON_RETURNS_COLUMN_MAP_INV)
    df = df[[c for c in OZON_RETURNS_COLUMN_MAP_INV.values() if c in df.columns]]
    logger.info(f"Ozon returns: прочитано {len(df)} строк из БД")
    return df

def _clean_value(col_name: str, value):
    if value is None or (isinstance(value, float) and np.isnan(value)) or pd.isna(value):
        return None
    if col_name in ID_LIKE_COLUMNS and isinstance(value, float):
        return str(int(value))
    return value


def _clean_records(df: pd.DataFrame) -> list[dict]:
    return [
        {col: _clean_value(col, val) for col, val in row.items()}
        for row in df.to_dict(orient='records')
    ]