import numpy as np
import pandas as pd
from sqlalchemy import text

from db import engine
from logger import setup_logger

logger = setup_logger("my_app")

# Маппинг: Excel-колонка → DB-колонка
COLUMN_MAP = {
    'Заказ': 'order_ref',
    'Заказ.Номер': 'order_number',
    'Заказ.Дата': 'order_date',
    'Заказ.ФИО': 'order_fio',
    'Заказ отменен': 'order_is_canceled',
    'Заказ.Причина отказа': 'cancel_reason',
    'Документ продажи': 'doc_sale',
    'Документ возврата': 'doc_return',
    'Текущий статус': 'status',
    'Сумма заказа': 'order_sum',
    'Ссылка.Стоимость доставки': 'delivery_cost',
    'Источник заказа': 'order_source',
    'Склад отправитель': 'sender_warehouse',
    'Заказ.Магазин': 'order_shop',
    'Заказ.Контактное лицо': 'contact_person',
    'Заказ.Пункт забора': 'pickup_point',
    'Заказ.Ответственный за доставку': 'delivery_responsible',
    'Заказ.Отправитель': 'sender',
    'Заказ.Номер отправления': 'posting_number',
    'Номенклатура': 'nomenclature',
    'Номенклатура.Артикул': 'article',
    'Характеристика номенклатуры': 'characteristic',
    'Номенклатура.Фирма производитель': 'brand',
    'Цена': 'price',
    'Количество': 'quantity',
    'Сумма продажи': 'sale_sum',
    'Сумма возврата': 'return_sum',
    'Документ продажи.Дата': 'doc_sale_date',
    'Документ возврата.Дата': 'doc_return_date',
    'Себестоимость возврата': 'cost_of_return',
    'Себестоимость продажи': 'cost_of_sale',
    'Ссылка.Способ доставки': 'delivery_method',
    'Заказ.Проект': 'project',
    'Номенклатура.Номенклатурная группа': 'nomenclature_group',
    'Номенклатура.Вид номенклатуры производителя': 'nomenclature_type',
    'Номенклатура.Вид номенклатуры производителя.Вид товара': 'product_type',
    'Номенклатура.Пол': 'gender',
    'Заказ.Пункт выдачи.Город': 'pickup_city',
    'Заказ.Магазин.Город': 'shop_city',
    'Сумма РРЦПродажи': 'rrc_sale_sum',
    'Сумма РРЦВозврата': 'rrc_return_sum',
    'Заказ.Источник': 'source',
    'Заказ.Продавец': 'seller',
    'Заказ.Комментарий заказчика': 'customer_comment',
    'ЗаказКомментарий менеджера': 'manager_comment',
    'Заказ.Email': 'email',
    'Заказ.Телефон': 'phone',
    'Заказ.Адрес': 'address',
    'Заказ.Заказ оплачен на сайте': 'paid_online',
    'Заказ.Промокод': 'promo_code',
    'Заказ.Ответственный магазин': 'responsible_shop',
    'Заказ.Продавец.Код': 'seller_code',
    'Заказ.Номер накладной возврата 1': 'return_invoice_1',
    'Заказ.Номер накладной возврата 2': 'return_invoice_2',
    'Документ комиссионера оплаты': 'commission_doc_sale',
    'Документ комиссионера возврат': 'commission_doc_return',
    'Сумма комиссионера продажи': 'commission_sale_sum',
    'Сумма комиссионера возврата': 'commission_return_sum',
    'Количество продажи': 'quantity_sale',
    'Количество возвраты': 'quantity_return',
    'Заказ.Канал': 'canal',
}

COLUMN_MAP_INV = {v: k for k, v in COLUMN_MAP.items()}

# PK для upsert — уникально идентифицирует строку в файле
PK_COLUMNS = ('order_number', 'article', 'characteristic')


def upsert_base_orders(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        logger.info("Нет данных Base для записи в БД")
        return

    df = df.rename(columns=COLUMN_MAP)
    df = df[[c for c in COLUMN_MAP.values() if c in df.columns]]
    records = _clean_records(df)

    columns = list(df.columns)
    placeholders = ', '.join(f':{c}' for c in columns)
    update_clause = ', '.join(
        f'{c} = VALUES({c})' for c in columns if c not in PK_COLUMNS
    )

    query = text(f"""
        INSERT INTO base_orders ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """)

    with engine.begin() as conn:
        conn.execute(query, records)

    logger.info(f"Base orders: записано/обновлено {len(records)} строк в БД")


def read_base_orders() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM base_orders"), conn)
    df = df.rename(columns=COLUMN_MAP_INV)
    df = df[[c for c in COLUMN_MAP_INV.values() if c in df.columns]]
    logger.info(f"Base orders: прочитано {len(df)} строк из БД")
    return df


def _clean_value(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def _clean_records(df: pd.DataFrame) -> list[dict]:
    return [
        {col: _clean_value(val) for col, val in row.items()}
        for row in df.to_dict(orient='records')
    ]