from dataclasses import asdict, dataclass


@dataclass
class ColumnsMainDTO:
    shop_name: str = 'Партнер'
    id: str = 'Номер заказа'
    created_at: str = 'Дата создания'
    updated_at: str = 'Дата изменения'
    status: str = 'Статус'
    sku: str = 'Артикул товара'
    description: str = 'Описание товара'
    brand: str = 'Бренд'
    size: str = 'Размер'
    status_product: str = 'Статус товара'
    payment_method: str = 'Метод оплаты'
    total_discount: str = 'Итого сумма скидок'
    sale_price: str = 'Цена со скидкой'
    paid_price: str = 'Цена продажи'
    base_price: str = 'Цена без скидки'
    coupon_discount: str = 'Скидка по купону'
    loyalty_discount: str = 'Скидка по лояльности'
    partner_agreed_discount: str = 'Скидка согласованная с партнером'
    other_discounts: str = 'Прочие скидки'
    platform_discounts: str = 'Платформенные скидки'
    partner_agreed_price: str = 'Цена согласованная с партнером'
    city: str = 'Населенный пункт'
    shipping_method_code: str = 'Метод доставки'
