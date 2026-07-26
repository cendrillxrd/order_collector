from dataclasses import asdict, dataclass


@dataclass
class MedDTO:
    offer_id: str = 'Offer ID'
    seller_articul: str = 'Артикул'
    barcode: str = 'Баркод'
    size: str = 'Размер'
    brand: str = 'Бренд'
    collection: str = 'Коллекция'
