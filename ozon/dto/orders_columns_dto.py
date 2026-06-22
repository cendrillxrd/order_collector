from dataclasses import asdict, dataclass


@dataclass
class OrdersColumnsDTO:
    order_number: str = 'Номер заказа'
    posting_number: str = 'Номер отправления'
    created_at: str = 'Принят в обработку'
    status: str = 'Статус'
    post_date: str = 'Дата доставки'
    canceled_date: str = 'Дата отмены'
    price: str = 'Сумма отправления'
    brand: str = 'Бренд'
    name: str = 'Название товара'
    color: str = 'Цвет товара'
    sku: str = 'SKU'
    offer_id: str = 'Артикул'
    quantity: str = 'Количество'
    price_without_discount: str = 'Цена товара до скидок'
    discount: str = 'Скидка %'