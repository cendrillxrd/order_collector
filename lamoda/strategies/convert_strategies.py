from abc import ABC, abstractmethod
from io import BytesIO
from typing import Union

import pandas as pd

from lamoda.config import BASE_COLUMNS_NAME
from lamoda.dto.columns_main_dto import ColumnsMainDTO
from lamoda.utils.save_helper import correct_columns_name


class ConverterStrategy(ABC):
    def __init__(self):
        self.columns_main = ColumnsMainDTO()

    @abstractmethod
    def converting(self, data) -> Union[pd.DataFrame, list]:
        pass

class ConvOrderStrategy(ConverterStrategy):
    def converting(self, data: dict) -> list:
        df = pd.DataFrame(data)
        order_ids = df['id'].tolist()
        return order_ids

class ConvAllNomenclaturesStrategy(ConverterStrategy):
    def converting(self, data: dict) -> pd.DataFrame:
        df = pd.json_normalize(data)
        df.columns = df.columns.str.replace('nomenclature.', '', regex=False)
        columns_name = [column for column in df.columns if column in BASE_COLUMNS_NAME]
        columns_rename = {k: BASE_COLUMNS_NAME.get(k) for k in columns_name}
        df.rename(columns_rename,
                  inplace=True,
                  axis=1)
        df_without_unnecessary_columns = df[
            [self.columns_main.sku,
             self.columns_main.brand,
             ]]
        return df_without_unnecessary_columns

class ConvOrderInfoStrategy(ConverterStrategy):
    def converting(self, data: list[dict]) -> pd.DataFrame:
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

        columns_name = [column for column in df.columns if column in BASE_COLUMNS_NAME]
        columns_rename = {k: BASE_COLUMNS_NAME.get(k) for k in columns_name}
        df.rename(columns_rename,
                  inplace=True,
                  axis=1)

        return df

class ConvMEDCollections(ConverterStrategy):
    def converting(self, data, **kwargs) -> pd.DataFrame:
        """Преобразует данные о коллекциях на меде в DataFrame"""
        med_collections_df = pd.read_excel(BytesIO(data.content))

        med_collections_df = correct_columns_name(med_collections_df)

        med_collections_df_without_unnecessary_columns = med_collections_df[
            [self.columns_main.supplier_parent_sku, self.columns_main.brand]]
        med_collections_df_without_unnecessary_columns.drop_duplicates(
            subset=self.columns_main.supplier_parent_sku, inplace=True)
        med_collections_df_without_unnecessary_columns.reset_index(inplace=True, drop=True)
        return med_collections_df_without_unnecessary_columns
