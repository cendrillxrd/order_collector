from typing import Literal

import pandas as pd
from pandas import DataFrame

from config import MAIN_DIR
from lamoda.config import (NOMENCLATURE_DAY_FILE_NAME, NOMENCLATURE_FILE_NAME,
                           ORDERS_FILE_NAME, BASE_ORDERS_FILE_NAME, BASE_ORDERS_FILE_NAME_SMART_PREMIUM)
from lamoda.dto.columns_main_dto import ColumnsMainDTO
from lamoda.dto.info_dto import InfoDTO
from lamoda.service.redaction import RedactionService


class InfoRedactor:
    def __init__(self, market_type: str = Literal['ufo', 'smart_premium']):
        self.market_type = market_type
        self.red = RedactionService()
        self.columns = ColumnsMainDTO()

    def redact_info(self, info: InfoDTO, get_new_info: bool = False) -> pd.DataFrame:
        if get_new_info:
            orders_with_brand = self.red.merge_orders_with_brand(info.orders_month, info.nomenclature)
            orders_all_info = self.red.merge_orders_info(info.all_orders, orders_with_brand)
            if self.market_type == 'ufo':
                orders_all_info.to_excel(f'{MAIN_DIR}/{BASE_ORDERS_FILE_NAME}.xlsx', index=False)
            elif self.market_type == 'smart_premium':
                orders_all_info.to_excel(f'{MAIN_DIR}/{BASE_ORDERS_FILE_NAME_SMART_PREMIUM}.xlsx', index=False)
            else:
                raise ValueError('market_type must be ufo or smart_premium')
            orders_main_info = self.red.orders_main_info(orders_all_info)

            returns_main_info = self.red.returns_main_info(orders_all_info)

            agg_table = self.red.merge_main_info(orders_main_info, returns_main_info)

            return agg_table
        else:
            if self.market_type == 'ufo':
                orders_all_info = pd.read_excel(f'{MAIN_DIR}/{BASE_ORDERS_FILE_NAME}.xlsx')
            elif self.market_type == 'smart_premium':
                orders_all_info = pd.read_excel(f'{MAIN_DIR}/{BASE_ORDERS_FILE_NAME_SMART_PREMIUM}.xlsx')
            else:
                raise ValueError('market_type must be ufo or smart_premium')

            orders_main_info = self.red.orders_main_info(orders_all_info)

            returns_main_info = self.red.returns_main_info(orders_all_info)

            agg_table = self.red.merge_main_info(orders_main_info, returns_main_info)

            return agg_table
