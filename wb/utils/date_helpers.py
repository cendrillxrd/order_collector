from datetime import datetime, timedelta


def get_weeks_range(weeks_back: int) -> tuple[str, str]:
    """
    Возвращает диапазон дат за N последних полных недель (пн-вс),
    не включая текущую неделю.

    Args:
        weeks_back: количество полных недель в диапазоне

    Returns:
        tuple: (дата_начала, дата_конца) в формате 'YYYY-MM-DD'
    """
    today = datetime.now()
    current_monday = today - timedelta(days=today.weekday())
    last_monday = current_monday - timedelta(days=7)
    last_sunday = last_monday + timedelta(days=6)
    start_monday = current_monday - timedelta(days=7 * weeks_back)
    return start_monday.strftime('%Y-%m-%d'), last_sunday.strftime('%Y-%m-%d')