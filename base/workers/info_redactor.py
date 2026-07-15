import pandas as pd

from base.dto.columns_main_dto import ColumnsBaseDTO
from base.repositories.db_repository import read_base_orders
from base.services import redaction


class InfoRedactor:
    def __init__(self):
        self.columns = ColumnsBaseDTO()

    def redact_info(self) -> pd.DataFrame:
        df = read_base_orders()

        site_filters = {
            'Проект THE HILLS': 'Сайт THE HILLS',
            'Проект MARC CONY': 'Сайт MC',
            'Проект VAN MICH': 'Сайт VAN MICH',
            'МЁД': 'Сайт Мёд',
            'Приложение': 'Приложение',
            'Проект VipAvenue': 'VipAvenue',
        }

        result = []
        for project_name, filter_value in site_filters.items():
            subset = df[df[self.columns.canal] == filter_value].copy()
            if subset.empty:
                continue
            orders = redaction.correction_dataframe_orders(subset, project_name)
            result.append(orders)

        return pd.concat(result)