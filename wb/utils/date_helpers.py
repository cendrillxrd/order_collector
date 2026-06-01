from datetime import datetime, timedelta

def get_week_number() -> int:
    """Возвращает номер недели."""
    return datetime.now().isocalendar()[1]

def get_year() -> int:
    """Возвращает текущий год."""
    return datetime.now().year

def get_month() -> int:
    """Возвращает номер текущего месяца (1-12)."""
    return datetime.now().month

def get_today_date() -> str:
    """Возвращает текущую дату в формате 'YYYY-MM-DD'."""
    return datetime.now().strftime('%Y-%m-%d')


def get_last_week_dates() -> tuple[str, str]:
    """
    Возвращает даты начала и конца прошлой недели в формате 'YYYY-MM-DD'.

    Returns:
        tuple: (дата_начала_недели, дата_конца_недели)
    """

    today = datetime.now()
    # Находим понедельник текущей недели
    current_monday = today - timedelta(days=today.weekday())
    # Понедельник прошлой недели
    last_monday = current_monday - timedelta(days=7)
    # Воскресенье прошлой недели
    last_sunday = last_monday + timedelta(days=6)

    return last_monday.strftime('%Y-%m-%d'), last_sunday.strftime('%Y-%m-%d')


from datetime import datetime, timedelta


def get_two_weeks_range() -> tuple[str, str]:
    """
    Возвращает диапазон дат:
    - Начало позапрошлой недели (понедельник)
    - Конец прошлой недели (воскресенье)

    Returns:
        tuple: (дата_начала_позапрошлой_недели, дата_конца_прошлой_недели) в формате 'YYYY-MM-DD'
    """
    today = datetime.now()

    # Находим понедельник текущей недели
    current_monday = today - timedelta(days=today.weekday())

    # Понедельник прошлой недели
    last_monday = current_monday - timedelta(days=7)

    # Понедельник позапрошлой недели
    week_before_last_monday = last_monday - timedelta(days=7)

    # Воскресенье прошлой недели
    last_sunday = last_monday + timedelta(days=6)

    return week_before_last_monday.strftime('%Y-%m-%d'), last_sunday.strftime('%Y-%m-%d')

def get_previous_week_date() -> str:
    """Возвращает вчерашнюю дату в формате 'YYYY-MM-DD'."""
    return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

def get_last_two_months() -> tuple[str, str, str, str]:
    """Возвращает даты для сравнения текущего и прошлого месяца в формате 'YYYY-MM-DD'."""
    current_end = datetime.now()
    current_start = current_end - timedelta(days=30)
    past_end = current_start - timedelta(days=1)
    past_start = current_start - timedelta(days=30)
    return (
        current_start.strftime('%Y-%m-%d'),
        current_end.strftime('%Y-%m-%d'),
        past_start.strftime('%Y-%m-%d'),
        past_end.strftime('%Y-%m-%d')
    )

def is_sunday() -> bool:
    """Возвращает True, если сегодня воскресенье."""
    return datetime.now().isoweekday() == 7

def is_saturday():
    """Возвращает True, если сегодня суббота."""
    return datetime.now().isoweekday() == 6