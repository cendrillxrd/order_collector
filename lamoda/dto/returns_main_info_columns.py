from dataclasses import asdict, dataclass


@dataclass
class ReturnsMainInfoColumnsDTO:
    market: str = 'Площадка'
    year: str = 'Год'
    month: str = 'Месяц'
    week: str = 'Неделя'
    brand: str = 'Бренд'
    returned_sum: str = 'Возвраты на сумму'
    returned: str = 'Возвраты шт'
