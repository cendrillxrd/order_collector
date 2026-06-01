from dataclasses import asdict, dataclass


@dataclass
class  ReturnsColumnsDTO:
    id: str = 'ID возврата'
    order_number: str = 'Номер заказа'
    posting_number: str = 'Номер отправления'
    return_date: str = 'Дата возврата'
    type: str = 'Тип возврата'
    return_reason_name: str = 'Причина возврата'
    schema: str = 'Схема возврата'
    sku: str = 'SKU'
    offer_id: str = 'Артикул'
    name: str = 'Название товара'
    price: str = 'Сумма отправления'
    quantity: str = 'Количество'
    brand: str = 'Бренд'