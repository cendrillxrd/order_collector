import pandas as pd

from base.repositories.db_repository import read_base_orders
from columns_common_dto import ColumnsCommonDTO, asdict

class InfoBaseCommonRedact:
    def __init__(self):
        self.common_info_columns = ColumnsCommonDTO()

    def redact(self):
        df = read_base_orders()
        df[self.common_info_columns.order_date] = pd.to_datetime(
            df[self.common_info_columns.order_date], errors='coerce'
        )
        df[self.common_info_columns.year] = df[self.common_info_columns.order_date].dt.year
        df[self.common_info_columns.month] = df[self.common_info_columns.order_date].dt.month
        df[self.common_info_columns.week] = df[self.common_info_columns.order_date].dt.isocalendar().week
        df[self.common_info_columns.order_is_canceled] = df[self.common_info_columns.order_is_canceled].isin(['v'])
        columns_to_fillna = [self.common_info_columns.sale_quantity, self.common_info_columns.return_quantity,
                             self.common_info_columns.sale_sum, self.common_info_columns.return_sum]
        for col in columns_to_fillna:
            df[col] = df[col].fillna(0)
        df[self.common_info_columns.shipping_sum] = df[self.common_info_columns.sale_sum]
        df[self.common_info_columns.returned_sum] = df[self.common_info_columns.return_sum]
        df = df[[col for col in asdict(self.common_info_columns).values() if col in df.columns]].copy()
        return df