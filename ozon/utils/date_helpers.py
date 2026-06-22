from dateutil.relativedelta import relativedelta

def date_month_ago():
    """
    Возвращает дату месяц назад в формате ISO 8601 с Z (UTC)
    """
    now = datetime.now()
    month_ago = now - relativedelta(months=1)
    month_ago = month_ago.replace(hour=0, minute=0, second=0, microsecond=0)
    return month_ago.strftime("%Y-%m-%dT%H:%M:%SZ")


def end_of_last_week():
    """
    Возвращает дату конца прошлой недели (воскресенье, 23:59:59)
    в формате ISO 8601 с Z (UTC)
    """
    now = datetime.now(timezone.utc)
    # Находим текущий день недели (понедельник=0, воскресенье=6)
    current_weekday = now.weekday()

    # Вычисляем сколько дней до прошлого воскресенья
    days_to_last_sunday = current_weekday + 1

    # Получаем прошлое воскресенье
    last_sunday = now - timedelta(days=days_to_last_sunday)

    # Устанавливаем время на 23:59:59
    end_of_last_week = datetime(
        last_sunday.year, last_sunday.month, last_sunday.day,
        23, 59, 59,
        tzinfo=timezone.utc
    )

    return end_of_last_week.strftime("%Y-%m-%dT%H:%M:%SZ")

def get_today_date() -> str:
    """Возвращает текущую дату в формате 'YYYY-MM-DD'."""
    return datetime.now().strftime("%Y-%m-%d")

def get_today_date_for_orders():
    return datetime.now(timezone.utc).isoformat()

def get_3_week_ago_date_for_orders():
    week_ago = datetime.now(timezone.utc) - timedelta(days=21)
    return week_ago.isoformat()

def get_year() -> int:
    """Возвращает текущий год."""
    return datetime.now().year

def get_month() -> int:
    """Возвращает номер текущего месяца (1-12)."""
    return datetime.now().month

def get_week_number() -> int:
    """Возвращает номер недели."""
    return datetime.now().isocalendar()[1]


from datetime import datetime, timezone, timedelta

def get_month_ago_start_of_day():
    """
    Возвращает дату месяц назад от текущей даты (начало дня)
    """
    today = datetime.now(timezone.utc)
    # Получаем дату месяц назад
    month_ago = today.replace(day=1) - timedelta(days=1)
    month_ago = month_ago.replace(day=min(today.day, month_ago.day))
    # Устанавливаем время на начало дня
    month_ago_start = month_ago.replace(hour=0, minute=0, second=0, microsecond=0)
    return month_ago_start

def get_last_sunday_end_of_day():
    """
    Возвращает дату конца воскресенья прошлой недели (23:59:59)
    """
    today = datetime.now(timezone.utc)
    # Находим последнее воскресенье
    days_until_last_sunday = (today.weekday() - 6) % 7
    if days_until_last_sunday == 0:
        days_until_last_sunday = 7
    last_sunday = today - timedelta(days=days_until_last_sunday)
    # Устанавливаем время на конец дня
    last_sunday_end = last_sunday.replace(hour=23, minute=59, second=59, microsecond=999999)
    return last_sunday_end

# Если нужна ISO строка, как в вашем примере:
def get_month_ago_iso():
    return get_month_ago_start_of_day().isoformat()

def get_last_sunday_end_iso():
    return get_last_sunday_end_of_day().isoformat()