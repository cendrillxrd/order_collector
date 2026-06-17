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