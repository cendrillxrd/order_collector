from typing import Literal

import pandas as pd

from config import MAIN_DIR, REMOTE_PATH
from lamoda.api_key import ApiKeyManager
from lamoda.lamoda_config import YANDEX_DISC_LAMODA_FILE_NAME, LOCAL_LAMODA_PATH, YANDEX_DISC_LAMODA_SP_FILE_NAME, \
    LOCAL_LAMODA_SP_PATH
from lamoda.dto.columns_main_dto import ColumnsMainDTO
from lamoda.dto.info_dto import InfoDTO
from lamoda.service.api_service import APIService
from lamoda.utils.date_helper import get_dates_for_request_by_month
from yandex_disk import download_file


class InfoCollector:
    def __init__(self, market_type: type[str] = Literal['ufo', 'smart_premium']):
        self.market_type = market_type
        self.api_key = ApiKeyManager(market_type)
        self.api = APIService(self.api_key)
        self.columns_main = ColumnsMainDTO()

    def collect_info(self) -> InfoDTO:
        # start_date = '2026-06-10'
        # end_date = '2026-06-10'
        start_date, end_date = get_dates_for_request_by_month()

        orders_month = self.api.get_orders_info_by_products(start_date=start_date, end_date=end_date)
        if self.market_type == 'ufo':
            download_file(REMOTE_PATH + YANDEX_DISC_LAMODA_FILE_NAME, LOCAL_LAMODA_PATH)
            all_orders = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_LAMODA_FILE_NAME}')
        elif self.market_type == 'smart_premium':
            download_file(REMOTE_PATH + YANDEX_DISC_LAMODA_SP_FILE_NAME, LOCAL_LAMODA_SP_PATH)
            all_orders = pd.read_excel(f'{MAIN_DIR}{YANDEX_DISC_LAMODA_SP_FILE_NAME}')
        else:
            raise ValueError('market_type must be ufo or smart_premium')

        dates = orders_month[self.columns_main.created_at].unique().tolist()
        result = []
        for date in dates:
            temp_orders = orders_month[orders_month[self.columns_main.created_at] == date]
            nomenclature_info = self.api.get_all_nomenclatures(temp_orders[self.columns_main.sku].unique().tolist())
            result.append(nomenclature_info)
        nomenclature = pd.concat(result)
        nomenclature.drop_duplicates(inplace=True)

        return InfoDTO(
            nomenclature=nomenclature,
            orders_month=orders_month,
            all_orders=all_orders,
        )
