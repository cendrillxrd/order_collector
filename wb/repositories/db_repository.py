import pandas as pd
from sqlalchemy import text
import numpy as np
from db import engine
from logger import setup_logger

logger = setup_logger("my_app")

ID_LIKE_COLUMNS = {'barcode', 'nm_id', 'income_id', 'sticker', 'g_number', 'srid', 'sale_id'}

ORDERS_COLUMN_MAP = {
    'ID заказа': 'srid',
    'Дата заказа': 'order_date',
    'Дата последнего изменения': 'last_change_date',
    'Артикул продавца': 'supplier_article',
    'Размер': 'tech_size',
    'Баркод': 'barcode',
    'Цена без скидок': 'total_price',
    'Скидка продавца': 'discount_percent',
    'Цена со скидкой продавца': 'price_with_discount',
    'Склад': 'warehouse_name',
    'Номер поставки': 'income_id',
    'Артикул WB': 'nm_id',
    'Предмет': 'subject',
    'Категория': 'category',
    'Бренд': 'brand',
    'ID корзины покупателя': 'g_number',
    'ID стикера': 'sticker',
    'Отменен': 'is_canceled',
}

SALES_COLUMN_MAP = {
    'Дата продажи': 'sale_date',
    'Дата последнего изменения': 'last_change_date',
    'Артикул продавца': 'supplier_article',
    'Размер': 'tech_size',
    'Баркод': 'barcode',
    'Цена без скидок': 'total_price',
    'Скидка продавца': 'discount_percent',
    'Склад': 'warehouse_name',
    'Страна': 'country_name',
    'Округ': 'oblast_okrug_name',
    'Регион': 'region_name',
    'Номер поставки': 'income_id',
    'Уникальный ID продажи/возврата (S - продажа R - возврат (на склад WB))': 'sale_id',
    'Скидка WB': 'spp',
    'К перечислению продавцу': 'for_pay',
    'Фактическая цена с учетом всех скидок': 'finished_price',
    'Цена со скидкой продавца': 'price_with_disc',
    'Артикул WB': 'nm_id',
    'Предмет': 'subject',
    'Категория': 'category',
    'Бренд': 'brand',
    'ID корзины покупателя': 'g_number',
    'ID стикера': 'sticker',
    'ID заказа': 'srid',
}


def upsert_orders(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        logger.info("Нет новых заказов WB для записи в БД")
        return

    df = df.rename(columns=ORDERS_COLUMN_MAP)
    df = df[[c for c in ORDERS_COLUMN_MAP.values() if c in df.columns]]
    df = df.drop_duplicates(subset='srid')
    records = _clean_records(df)

    columns = list(df.columns)
    placeholders = ', '.join(f':{c}' for c in columns)
    update_clause = ', '.join(f'{c} = VALUES({c})' for c in columns if c != 'srid')

    query = text(f"""
        INSERT INTO wb_orders ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """)

    with engine.begin() as conn:
        conn.execute(query, records)

    logger.info(f"WB orders: записано/обновлено {len(records)} строк в БД")


def upsert_sales(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        logger.info("Нет новых продаж WB для записи в БД")
        return

    df = df.rename(columns=SALES_COLUMN_MAP)
    df = df[[c for c in SALES_COLUMN_MAP.values() if c in df.columns]]
    df = df.drop_duplicates(subset='sale_id')
    records = _clean_records(df)

    columns = list(df.columns)
    placeholders = ', '.join(f':{c}' for c in columns)
    update_clause = ', '.join(f'{c} = VALUES({c})' for c in columns if c != 'sale_id')

    query = text(f"""
        INSERT INTO wb_sales ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """)

    with engine.begin() as conn:
        conn.execute(query, records)

    logger.info(f"WB sales: записано/обновлено {len(records)} строк в БД")


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