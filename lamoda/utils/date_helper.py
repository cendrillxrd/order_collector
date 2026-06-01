from datetime import datetime, timedelta
from typing import Literal, Union

import pandas as pd
import pytz

def get_date_range_filter(start_date: datetime, end_date: datetime) -> str:
    """
    Возвращает диапазон дат в формате: createdAt>=<start_timestamp,end_timestamp>

    Args:
        start_date: Начальная дата (datetime с таймзоной)
        end_date: Конечная дата (datetime с таймзоной)

    Returns:
        str: Отформатированная строка для фильтра
    """
    start_timestamp = start_date.strftime('%Y%m%d%H%M%S')
    end_timestamp = end_date.strftime('%Y%m%d%H%M%S')
    return f"createdAt>=<{start_timestamp},{end_timestamp}"


# ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ КОНВЕРТАЦИИ ДАТ =============

def parse_date_string(date_str: str, is_date_from: bool) -> datetime:
    """
    Преобразует строку даты в datetime объект с временем 00:00:00 в московском часовом поясе

    Args:
        date_str: Дата в формате 'YYYY-MM-DD'
        is_date_from: True, если это дата начала

    Returns:
        datetime: Объект datetime с таймзоной
    """
    tz = pytz.timezone('Europe/Moscow')

    if is_date_from:
        input_date = datetime.strptime(date_str, '%Y-%m-%d')
        input_date = input_date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        input_date = datetime.strptime(date_str, '%Y-%m-%d')
        input_date = input_date.replace(hour=23, minute=59, second=59, microsecond=0)

    # Добавляем часовой пояс
    result_date = tz.localize(input_date)
    return result_date


def get_dates_for_request_by_month() -> tuple[str, str]:
    """
    Возвращает дату воскресенья прошлой недели и дату (30 дней назад) от этого воскресенья.

    Returns:
        tuple: (воскресенье_прошлой_недели, 30_дней_назад_от_воскресенья_прошлой_недели)
    """
    today = datetime.now()
    # Находим понедельник текущей недели
    current_monday = today - timedelta(days=today.weekday())
    # Понедельник прошлой недели
    last_monday = current_monday - timedelta(days=7)
    # Воскресенье прошлой недели
    last_sunday = last_monday + timedelta(days=6)

    # Дата 30 дней назад от воскресенья прошлой недели (приблизительный месяц)
    thirty_days_before = last_sunday - timedelta(days=30)

    return thirty_days_before.strftime('%Y-%m-%d'), last_sunday.strftime('%Y-%m-%d')


def filter_until_last_sunday(df, date_col):
    """Оставляет данные до конца прошлого воскресенья"""
    today = pd.Timestamp.now()
    # Идём к прошлому воскресенью
    last_sunday = today - pd.Timedelta(days=today.weekday() + 1)
    # Устанавливаем время 23:59:59
    last_sunday_end = last_sunday.replace(hour=23, minute=59, second=59)

    return df[df[date_col] <= last_sunday_end]