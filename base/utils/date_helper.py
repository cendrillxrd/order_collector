import pandas as pd


def filter_until_last_sunday(df, date_col):
    """Оставляет данные до конца прошлого воскресенья"""
    today = pd.Timestamp.now()
    # Идём к прошлому воскресенью
    last_sunday = today - pd.Timedelta(days=today.weekday() + 1)
    # Устанавливаем время 23:59:59
    last_sunday_end = last_sunday.replace(hour=23, minute=59, second=59)

    return df[df[date_col] <= last_sunday_end]