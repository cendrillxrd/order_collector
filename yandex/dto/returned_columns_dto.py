from dataclasses import asdict, dataclass


@dataclass
class ReturnedColumnsDTO:
    order_id: str = 'ID заказа'
    creation_date: str = 'Дата создания'
    update_date: str = 'Дата обновления'
    refundStatus: str = 'Статус возврата'
    amount: str = 'Сумма возврата'
    offer_id: str = 'Offer ID'
    count: str = 'Количество'
    comment: str = 'Комментарий'
    brand: str = 'Бренд'