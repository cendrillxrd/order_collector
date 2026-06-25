from abc import ABC, abstractmethod
from io import BytesIO
from typing import Union

import pandas as pd

from lamoda.lamoda_config import BASE_COLUMNS_NAME
from lamoda.dto.columns_main_dto import ColumnsMainDTO
from lamoda.utils.save_helper import correct_columns_name


class ConvertStrategy(ABC):
    def __init__(self):
        self.columns_main = ColumnsMainDTO()

    @abstractmethod
    def do_convert(self, data) -> Union[pd.DataFrame, list]:
        pass

class ConvOrderStrategy(ConvertStrategy):
    def do_convert(self, data: dict) -> list:
        df = pd.DataFrame(data)
        order_ids = df['id'].tolist()
        return order_ids

class ConvAllNomenclaturesStrategy(ConvertStrategy):
    def do_convert(self, data: dict) -> pd.DataFrame:
        df = pd.json_normalize(data)
        df.columns = df.columns.str.replace('nomenclature.', '', regex=False)

        df = correct_columns_name(df, BASE_COLUMNS_NAME)

        df_without_unnecessary_columns = df[
            [self.columns_main.sku,
             self.columns_main.brand,
             ]]
        return df_without_unnecessary_columns

class ConvOrderInfoStrategy(ConvertStrategy):
    def do_convert(self, data: list[dict]) -> pd.DataFrame:
        list_for_df = []

        for order in data:
            items = order['_embedded']['items']
            city = order['_embedded']['shippingAddress']['city']
            shipping_method_code = order['_embedded']['deliveryMethod']['shippingMethodCode']
            partner = order['_embedded']['partner']['shopName']

            for item in items:
                order_info = {
                    self.columns_main.shop_name: partner,
                    self.columns_main.id: order['id'],
                    self.columns_main.payment_method: order['paymentMethod'],
                    self.columns_main.status: order['status'],
                    self.columns_main.created_at: order['createdAt'],
                    self.columns_main.updated_at: order['updatedAt'],
                    self.columns_main.shipping_method_code: shipping_method_code,
                    self.columns_main.city: city,
                }
                item['status_product'] = item.pop('status')
                item['id_item_order'] = item.pop('id')
                order_info.update(item)

                list_for_df.append(order_info)

        df = pd.DataFrame(list_for_df)

        df = correct_columns_name(df, BASE_COLUMNS_NAME)
        return df
