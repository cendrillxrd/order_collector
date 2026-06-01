from dataclasses import asdict, dataclass


@dataclass
class OrdersMainInfoColumnsDTO:
    market: str = 'Площадка'
    year: str = 'Год'
    month: str = 'Месяц'
    week: str = 'Неделя'
    brand: str = 'Бренд'
    sum_orders: str = 'Сумма заказов'
    total_orders: str = 'Заказано шт'
    returned_sum: str = 'Возвраты на сумму'
    returned: str = 'Возвраты шт'
    total_main_orders: str = 'Количество заказов'
