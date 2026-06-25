from dataclasses import asdict, dataclass, field

from lamoda.lamoda_config import LIMIT_NOMENCLATURE


@dataclass
class NomenclatureDTO:
    jsonrpc: str = '2.0'
    id: str = None
    method: str = None
    params: dict = field(default_factory=lambda: {
        'country': 'RU',
        'page': 1,
        'limit': LIMIT_NOMENCLATURE,
        "filter": [
            {
                "key": "supplierSku",
                "operator": "IN",
            }
        ]
    })
