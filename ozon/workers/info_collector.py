import pandas as pd

from config import MAIN_DIR
from ozon.config import BASE_ORDERS_FILE_NAME, BASE_RETURNS_FILE_NAME
from ozon.dto.info_dto import InfoDTO
from ozon.services.med import MEDService
from ozon.services.ozon_service import OzonService

class InfoCollector:
    def __init__(self):
        self.ozon_service = OzonService()
        self.med = MEDService()

    def collect_info(self) -> InfoDTO:
        cards_info = self.ozon_service.get_cards_info()
        returns = self.ozon_service.get_returns()
        all_returns = pd.read_excel(f'{MAIN_DIR}/{BASE_RETURNS_FILE_NAME}.xlsx')
        orders = self.ozon_service.get_orders()
        all_orders = pd.read_excel(f'{MAIN_DIR}/{BASE_ORDERS_FILE_NAME}.xlsx')

        return InfoDTO(
            cards_info=cards_info,
            orders=orders,
            returns=returns,
            all_orders=all_orders,
            all_returns=all_returns,
        )