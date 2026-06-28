from typing import Literal

import pandas as pd
from config import MAIN_DIR, REMOTE_PATH
from lamoda.lamoda_config import (YANDEX_DISC_LAMODA_FILE_NAME, LOCAL_LAMODA_PATH, YANDEX_DISC_LAMODA_SP_FILE_NAME,
                                  LOCAL_LAMODA_SP_PATH)
from lamoda.dto.columns_main_dto import ColumnsMainDTO
from lamoda.dto.info_dto import InfoDTO
from lamoda.repositories.db_repository import upsert_lamoda_orders, read_lamoda_orders
from lamoda.service.redaction import RedactionService
from yandex_disk import download_file, upload_file


class InfoRedactor:
    def __init__(self, market_type: type[str] = Literal['ufo', 'smart_premium']):
        self.market_type = market_type
        self.red = RedactionService()
        self.columns = ColumnsMainDTO()

    def redact_info(self, info: InfoDTO, get_new_info: bool = False) -> pd.DataFrame:
        if get_new_info:
            orders_with_brand = self.red.merge_orders_with_brand(info.orders_month, info.nomenclature)
            upsert_lamoda_orders(orders_with_brand, self.market_type)

        orders_all_info = read_lamoda_orders(self.market_type)

        if get_new_info:
            file_name = YANDEX_DISC_LAMODA_FILE_NAME if self.market_type == 'ufo' else YANDEX_DISC_LAMODA_SP_FILE_NAME
            orders_all_info.to_excel(f'{MAIN_DIR}{file_name}', index=False)
            upload_file(f'{MAIN_DIR}{file_name}', REMOTE_PATH + file_name)

        orders_main_info = self.red.orders_main_info(orders_all_info)
        returns_main_info = self.red.returns_main_info(orders_all_info)

        agg_table = self.red.merge_main_info(orders_main_info, returns_main_info)
        return agg_table
