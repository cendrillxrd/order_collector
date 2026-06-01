from dataclasses import asdict, dataclass


@dataclass
class OrdersColumnsDTO:
    date: str = 'Дата заказа'
    lastChangeDate: str = 'Дата последнего изменения'
    supplierArticle: str = 'Артикул продавца'
    techSize: str = 'Размер'
    barcode: str = 'Баркод'
    totalPrice: str = 'Цена без скидок'
    discountPercent: str = 'Скидка продавца'
    warehouseName: str = 'Склад'
    incomeID: str = 'Номер поставки'
    nmId: str = 'Артикул WB'
    subject: str = 'Предмет'
    category: str = 'Категория'
    brand: str = 'Бренд'
    gNumber: str = 'ID корзины покупателя'
    sticker: str = 'ID стикера'
    isCanceled: str = 'Отменен'
    srid: str = 'ID заказа'
    price_with_discount: str = 'Цена со скидкой'