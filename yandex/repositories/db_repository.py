import numpy as np
import pandas as pd
from sqlalchemy import text

from db import engine
from logger import setup_logger

logger = setup_logger("my_app")

ID_LIKE_COLUMNS = {'order_id', 'external_order_id', 'campaign_id'}

YANDEX_ORDERS_COLUMN_MAP = {
    'ID заказа': 'order_id',
    'ID магазина': 'campaign_id',
    'Модель работы': 'program_type',
    'Внешний ID заказа': 'external_order_id',
    'Статус': 'status',
    'Этап обработки': 'substatus',
    'Дата создания': 'creation_date',
    'Дата обновления': 'update_date',
    'Тип оплаты': 'payment_type',
    'Метод оплаты': 'payment_method',
    'Fake заказ': 'fake',
    'Offer ID': 'offer_id',
    'Бренд': 'brand',
    'Количество': 'count',
    'Цена': 'price',
    'Название': 'name',
    'Комментарий': 'notes',
}

YANDEX_RETURNS_COLUMN_MAP = {
    'ID заказа': 'order_id',
    'Дата создания': 'creation_date',
    'Дата обновления': 'update_date',
    'Статус возврата': 'refund_status',
    'Сумма возврата': 'amount',
    'Offer ID': 'offer_id',
    'Количество': 'count',
    'Комментарий': 'comment',
    'Бренд': 'brand',
}


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


def upsert_yandex_orders(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        logger.info("Нет новых заказов Yandex для записи в БД")
        return

    df = df.rename(columns=YANDEX_ORDERS_COLUMN_MAP)
    df = df[[c for c in YANDEX_ORDERS_COLUMN_MAP.values() if c in df.columns]]
    df = df.copy()
    df['position'] = df.groupby(['order_id', 'offer_id']).cumcount()
    records = _clean_records(df)

    columns = list(df.columns)
    placeholders = ', '.join(f':{c}' for c in columns)
    update_clause = ', '.join(
        f'{c} = VALUES({c})'
        for c in columns
        if c not in ('order_id', 'offer_id', 'position')
    )

    query = text(f"""
        INSERT INTO yandex_orders ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """)

    with engine.begin() as conn:
        conn.execute(query, records)

    logger.info(f"Yandex orders: записано/обновлено {len(records)} строк в БД")


def upsert_yandex_returns(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        logger.info("Нет новых возвратов Yandex для записи в БД")
        return

    df = df.rename(columns=YANDEX_RETURNS_COLUMN_MAP)
    df = df[[c for c in YANDEX_RETURNS_COLUMN_MAP.values() if c in df.columns]]
    df = df.copy()
    df['position'] = df.groupby(['order_id', 'offer_id']).cumcount()
    records = _clean_records(df)

    columns = list(df.columns)
    placeholders = ', '.join(f':{c}' for c in columns)
    update_clause = ', '.join(
        f'{c} = VALUES({c})'
        for c in columns
        if c not in ('order_id', 'offer_id', 'position')
    )

    query = text(f"""
        INSERT INTO yandex_returns ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """)

    with engine.begin() as conn:
        conn.execute(query, records)

    logger.info(f"Yandex returns: записано/обновлено {len(records)} строк в БД")