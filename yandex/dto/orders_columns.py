from dataclasses import asdict, dataclass


@dataclass
class OrdersColumnsDTO:
    order_id: str = 'ID заказа'
    campaign_id: str = 'ID магазина'
    program_type: str = 'Модель работы'
    external_order_id: str = 'Внешний ID заказа'
    status: str = 'Статус'
    substatus: str = 'Этап обработки'
    creation_date: str = 'Дата создания'
    update_date: str = 'Дата обновления'
    payment_type: str = 'Тип оплаты'
    payment_method: str = 'Метод оплаты'
    fake: str = 'Fake заказ'
    offer_id: str = 'Offer ID'
    brand: str = 'Бренд'
    count: str = 'Количество'
    price: str = 'Цена'
    name: str = 'Название'
    notes: str = 'Комментарий'

