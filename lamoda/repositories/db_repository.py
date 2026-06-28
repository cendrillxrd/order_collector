from typing import Literal

import numpy as np
import pandas as pd
from sqlalchemy import text

from db import engine
from logger import setup_logger

logger = setup_logger("my_app")

ID_LIKE_COLUMNS = {'order_id', 'sku'}

LAMODA_ORDERS_COLUMN_MAP = {
    'Партнер': 'shop_name',
    'Номер заказа': 'order_id',
    'Дата создания': 'created_at',
    'Дата изменения': 'updated_at',
    'Статус': 'status',
    'Артикул товара': 'sku',
    'Описание товара': 'description',
    'Бренд': 'brand',
    'Размер': 'size',
    'Статус товара': 'status_product',
    'Метод оплаты': 'payment_method',
    'Итого сумма скидок': 'total_discount',
    'Цена со скидкой': 'sale_price',
    'Цена продажи': 'paid_price',
    'Цена без скидки': 'base_price',
    'Скидка по купону': 'coupon_discount',
    'Скидка по лояльности': 'loyalty_discount',
    'Скидка согласованная с партнером': 'partner_agreed_discount',
    'Прочие скидки': 'other_discounts',
    'Платформенные скидки': 'platform_discounts',
    'Цена согласованная с партнером': 'partner_agreed_price',
    'Населенный пункт': 'city',
    'Метод доставки': 'shipping_method_code',
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

LAMODA_ORDERS_COLUMN_MAP_INV = {v: k for k, v in LAMODA_ORDERS_COLUMN_MAP.items()}

def read_lamoda_orders(market_type: type[str] = Literal['ufo', 'smart_premium']) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT * FROM lamoda_orders WHERE market_type = :mt"),
            conn,
            params={'mt': market_type}
        )
    df = df.rename(columns=LAMODA_ORDERS_COLUMN_MAP_INV)
    df = df[[c for c in LAMODA_ORDERS_COLUMN_MAP_INV.values() if c in df.columns]]
    logger.info(f"Lamoda [{market_type}] orders: прочитано {len(df)} строк из БД")
    return df

def upsert_lamoda_orders(df: pd.DataFrame, market_type: type[str] = Literal['ufo', 'smart_premium']) -> None:
    if df is None or df.empty:
        logger.info(f"Нет новых заказов Lamoda [{market_type}] для записи в БД")
        return

    # Сохраняем position ДО rename и фильтрации
    position = df['position'].copy() if 'position' in df.columns else None

    df = df.rename(columns=LAMODA_ORDERS_COLUMN_MAP)
    df = df[[c for c in LAMODA_ORDERS_COLUMN_MAP.values() if c in df.columns]]
    df = df.copy()
    df['market_type'] = market_type

    if position is not None:
        df['position'] = position.values
    else:
        df['position'] = df.groupby(['order_id', 'sku']).cumcount()

    records = _clean_records(df)

    columns = list(df.columns)
    placeholders = ', '.join(f':{c}' for c in columns)
    update_clause = ', '.join(
        f'{c} = VALUES({c})'
        for c in columns
        if c not in ('order_id', 'sku', 'position', 'market_type')
    )

    query = text(f"""
        INSERT INTO lamoda_orders ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """)

    with engine.begin() as conn:
        conn.execute(query, records)

    logger.info(f"Lamoda orders [{market_type}]: записано/обновлено {len(records)} строк в БД")