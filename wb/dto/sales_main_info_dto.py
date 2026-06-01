from dataclasses import asdict, dataclass


@dataclass
class SalesMainInfoColumnsDTO:
    market: str = 'Площадка'
    year: str = 'Год'
    month: str = 'Месяц'
    week: str = 'Неделя'
    brand: str = 'Бренд'
    returned_sum: str = 'Возвраты на сумму'
    returned: str = 'Возвраты шт'
    total_main_orders: str = 'Количество заказов'