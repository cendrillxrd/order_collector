from dataclasses import asdict, dataclass

from lamoda.config import LIMIT_STOCK


@dataclass
class StockDTO:
    limit: int = LIMIT_STOCK
    page: int = 1
    withZeroQuantity: str = '0'
