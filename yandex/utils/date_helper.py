from datetime import datetime, timedelta

def get_current_week_monday() -> str:
    """
    Возвращает дату понедельника текущей недели в формате 'YYYY-MM-DD'.
    """
    today = datetime.now()
    # weekday(): понедельник = 0, воскресенье = 6
    monday = today - timedelta(days=today.weekday())
    return monday.strftime('%Y-%m-%d')

def get_last_week_sunday() -> str:
    """
    Возвращает дату воскресенья прошлой недели в формате 'YYYY-MM-DD'.
    """
    today = datetime.now()
    # weekday(): понедельник = 0, воскресенье = 6
    # Получаем понедельник текущей недели
    current_monday = today - timedelta(days=today.weekday())
    # Воскресенье прошлой недели = понедельник текущей недели - 1 день
    last_week_sunday = current_monday - timedelta(days=1)
    return last_week_sunday.strftime('%Y-%m-%d')

def get_date_30_days_before_last_week_end() -> str:
    """
    Возвращает дату на 30 дней дальше от даты конца прошлой недели в формате 'YYYY-MM-DD'.
    """
    last_week_end = datetime.strptime(get_current_week_monday(), '%Y-%m-%d')
    future_date = last_week_end - timedelta(days=30)
    return future_date.strftime('%Y-%m-%d')