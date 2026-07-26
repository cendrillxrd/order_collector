from functools import reduce
import pandas as pd

from columns_common_dto import ColumnsCommonDTO, asdict
from ozon.dto.orders_columns_dto import OrdersColumnsDTO
from ozon.dto.returns_columns_dto import ReturnsColumnsDTO
from ozon.repositories.db_repository import read_ozon_orders, read_ozon_returns
from med.services.med_service import MedService
from med.services.redaction_service import RedactionMedService

QUANTITY_RETURNS = 'Количество возвратов'

class InfoOZONCommonRedact:
    def __init__(self):
        self.returns_all_info_columns = ReturnsColumnsDTO()
        self.orders_all_info_columns = OrdersColumnsDTO()
        self.common_info_columns = ColumnsCommonDTO()
        self.med = MedService()
        self.red_med = RedactionMedService()

    def redact(self):
        #Обновления бд нет, работаю уже с готовыми данными
        orders_all_info = read_ozon_orders()
        returns_all_info = read_ozon_returns()

        med_collections = self.med.get_med_collections()
        collections_merged = reduce(self.red_med.merge_collections, med_collections)
        collections_merged.drop(columns='Бренд', inplace=True)
        collections_merged = collections_merged.rename(columns={'Артикул': 'Артикул продавца', 'Offer ID':'Артикул'})

        returns_all_info = returns_all_info[[self.returns_all_info_columns.posting_number, self.returns_all_info_columns.sku, self.returns_all_info_columns.quantity, self.returns_all_info_columns.return_date]].copy()
        returns_all_info = returns_all_info.rename(columns={self.returns_all_info_columns.quantity: QUANTITY_RETURNS})
        returns_all_info = (returns_all_info.groupby([self.returns_all_info_columns.posting_number, self.returns_all_info_columns.sku, self.returns_all_info_columns.return_date], as_index=False
                                                     )[QUANTITY_RETURNS].sum())
        #Объединяю данные
        orders_returns = pd.merge(orders_all_info, returns_all_info, on=[self.returns_all_info_columns.posting_number, self.returns_all_info_columns.sku], how='left')
        orders_returns[self.orders_all_info_columns.offer_id] = orders_returns[self.orders_all_info_columns.offer_id].astype(str)
        collections_merged[self.orders_all_info_columns.offer_id] = collections_merged[self.orders_all_info_columns.offer_id].astype(str)
        orders_returns_collections = pd.merge(orders_returns, collections_merged, on=self.orders_all_info_columns.offer_id , how='left')

        COLUMNS_NAME_TO_COMMON = {
            self.orders_all_info_columns.order_number: self.common_info_columns.order_id,
            #order
            self.orders_all_info_columns.created_at: self.common_info_columns.order_date,
            #customer_full_name
            #order_is_canceled
            #cancel_reason
            #doc_sale
            #doc_return
            self.orders_all_info_columns.status: self.common_info_columns.status,
            self.orders_all_info_columns.price: self.common_info_columns.order_sum,
            #cost_of_delivery
            #order_source
            #sender_warehouse
            #shop
            #posting_number
            self.orders_all_info_columns.name: self.common_info_columns.nomenclature,
            #
            'Артикул продавца': self.common_info_columns.article,
            'Размер': self.common_info_columns.characteristic_nomenclature,
            self.orders_all_info_columns.brand: self.common_info_columns.manufacturer,
            #price
            self.orders_all_info_columns.quantity: self.common_info_columns.quantity,
            #sale_sum
            #return_sum
            #sale_date
            self.returns_all_info_columns.return_date: self.common_info_columns.returned_date,
            #main_cost_of_return
            #main_cost_of_sale
            #delivery_method
            #project
            #nomenclature_group
            #manufacturer_nomenclature_type
            #manufacturer_nomenclature_product_type
            #gender
            #pickup_point_city
            #shop_city
            #rrc_sale_sum
            #rrc_return_sum
            #source
            #seller
            #customer_comment
            #manager_comment
            #email
            #phone
            #address
            #is_paid_on_site
            #promo_code
            #responsible_shop
            #seller_code
            #return_invoice_number_1
            #return_invoice_number_2
            #sale_quantity
            #return_quantity
            #canal
        }

        common_df = (
            orders_returns_collections.rename(columns=COLUMNS_NAME_TO_COMMON)
            .assign(
                    **{self.common_info_columns.year: lambda d: d[self.common_info_columns.order_date].dt.year},
                    **{self.common_info_columns.month: lambda d: d[self.common_info_columns.order_date].dt.month},
                    **{self.common_info_columns.week: lambda d: d[self.common_info_columns.order_date].dt.isocalendar().week},
                    **{self.common_info_columns.order: None},
                    **{self.common_info_columns.customer_full_name: 'Клиент OZON'},
                    **{self.common_info_columns.order_is_canceled: lambda d: d[self.common_info_columns.status].isin(
                        ['Отменён']).astype(int)},
                    **{self.common_info_columns.cancel_reason: None},
                    **{self.common_info_columns.doc_sale: None},
                    **{self.common_info_columns.doc_return: None},
                    **{self.common_info_columns.cost_of_delivery: None},
                    **{self.common_info_columns.order_source: 'OZON'},
                    **{self.common_info_columns.sender_warehouse: None},
                    **{self.common_info_columns.shop: 'OZON'},
                    **{self.common_info_columns.posting_number: None},
                    **{self.common_info_columns.price: lambda d: d[self.common_info_columns.order_sum] / d[self.common_info_columns.quantity]},
                    **{self.common_info_columns.return_quantity: lambda d: d[QUANTITY_RETURNS].fillna(0)},
                    **{self.common_info_columns.sale_quantity: lambda d: (d[self.common_info_columns.quantity] - d[
                        self.common_info_columns.return_quantity]).where(
                        d[self.common_info_columns.status].isin(['Доставлен']), 0)},
                    **{self.common_info_columns.sale_sum: lambda d: (d[self.common_info_columns.price] * d[self.common_info_columns.sale_quantity]).where(
                        d[self.common_info_columns.status].isin(['Доставлен']), 0)},
                    **{self.common_info_columns.shipping_sum: lambda d: d[self.common_info_columns.order_sum]},
                    **{self.common_info_columns.return_sum: lambda d: d[self.common_info_columns.price] * d[self.common_info_columns.return_quantity]},
                    **{self.common_info_columns.sale_date: lambda d: d[self.orders_all_info_columns.post_date].where(d[self.common_info_columns.sale_quantity]>0, None)},
                    **{self.common_info_columns.main_cost_of_return: None},
                    **{self.common_info_columns.main_cost_of_sale: None},
                    **{self.common_info_columns.delivery_method: None},
                    **{self.common_info_columns.project: 'OZON'},
                    **{self.common_info_columns.nomenclature_group: None},
                    **{self.common_info_columns.manufacturer_nomenclature_type: lambda d:
                        d[self.common_info_columns.nomenclature].str.split().str[0]},
                    **{self.common_info_columns.manufacturer_nomenclature_product_type: lambda d:
                        d[self.common_info_columns.nomenclature].str.split().str[0]},
                    **{self.common_info_columns.gender: None},
                    **{self.common_info_columns.pickup_point_city: None},
                    **{self.common_info_columns.shop_city: None},
                    **{self.common_info_columns.rrc_sale_sum: None},
                    **{self.common_info_columns.rrc_return_sum: None},
                    **{self.common_info_columns.source: 'OZON'},
                    **{self.common_info_columns.seller: None},
                    **{self.common_info_columns.customer_comment: None},
                    **{self.common_info_columns.manager_comment: None},
                    **{self.common_info_columns.email: None},
                    **{self.common_info_columns.phone: None},
                    **{self.common_info_columns.address: None},
                    **{self.common_info_columns.is_paid_on_site: None},
                    **{self.common_info_columns.promo_code: None},
                    **{self.common_info_columns.responsible_shop: None},
                    **{self.common_info_columns.seller_code: None},
                    **{self.common_info_columns.return_invoice_number_1: None},
                    **{self.common_info_columns.return_invoice_number_2: None},
                    **{self.common_info_columns.canal: 'OZON'},
                    **{self.common_info_columns.returned_sum: lambda d: d[self.common_info_columns.return_sum] + d[self.common_info_columns.order_sum].where(
                            d[self.common_info_columns.order_is_canceled] == 1, 0)}
                    )
        )

        common_df = common_df[
            [col for col in asdict(self.common_info_columns).values() if col in common_df.columns]].copy()

        common_df.to_excel('ozon_common.xlsx', index=False)
        return common_df
