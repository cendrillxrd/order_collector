from dataclasses import asdict, dataclass


@dataclass
class SalesColumnsDTO:
    date: str = 'Дата продажи'
    lastChangeDate: str = 'Дата последнего изменения'
    supplierArticle: str = 'Артикул продавца'
    techSize: str = 'Размер'
    barcode: str = 'Баркод'
    totalPrice: str = 'Цена без скидок'
    discountPercent: str = 'Скидка продавца'
    warehouseName: str = 'Склад'
    countryName: str = 'Страна'
    oblastOkrugName: str = 'Округ'
    regionName: str = 'Регион'
    incomeID: str = 'Номер поставки'
    saleID: str = 'Уникальный ID продажи/возврата (S - продажа R - возврат (на склад WB))'
    spp: str = 'Скидка WB'
    forPay: str = 'К перечислению продавцу'
    finishedPrice: str = 'Фактическая цена с учетом всех скидок'
    priceWithDisc: str = 'Цена со скидкой продавца'
    nmId: str = 'Артикул WB'
    subject: str = 'Предмет'
    category: str = 'Категория'
    brand: str = 'Бренд'
    gNumber: str = 'ID корзины покупателя'
    sticker: str = 'ID стикера'
    srid: str = 'ID заказа'