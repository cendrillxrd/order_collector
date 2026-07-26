from typing import Literal

from columns_common_dto import ColumnsCommonDTO, asdict
from lamoda.dto.columns_main_dto import ColumnsMainDTO
from lamoda.repositories.db_repository import read_lamoda_orders

CANCELLED_STATUSES = ['Returned', 'Canceled', 'Not delivered', 'Not bought']
RETURNED_STATUSES = ['Refunded', 'Refund necessary', 'Ready to refund']

class InfoLamodaCommonRedact:
    def __init__(self, market_type: type[str] = Literal['ufo', 'smart_premium']):
        self.orders_info_columns = ColumnsMainDTO()
        self.market_type = market_type
        self.common_info_columns = ColumnsCommonDTO()


    def redact(self):
        #Обновления бд нет, работаю уже с готовыми данными
        orders_all_info = read_lamoda_orders(self.market_type)

        COLUMNS_NAME_TO_COMMON = {
            self.orders_info_columns.id: self.common_info_columns.order_id,
            #order
            self.orders_info_columns.created_at: self.common_info_columns.order_date,
            #customer_full_name
            #order_is_canceled
            #cancel_reason
            #doc_sale
            #doc_return
            self.orders_info_columns.status_product: self.common_info_columns.status,
            self.orders_info_columns.partner_agreed_price: self.common_info_columns.order_sum,
            #cost_of_delivery
            #order_source
            #sender_warehouse
            #shop
            #posting_number
            self.orders_info_columns.description: self.common_info_columns.nomenclature,
            #article
            self.orders_info_columns.size: self.common_info_columns.characteristic_nomenclature,
            self.orders_info_columns.brand: self.common_info_columns.manufacturer,
            #price
            #quantity
            #sale_sum
            #return_sum
            #sale_date
            #returned_date
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
            self.orders_info_columns.city: self.common_info_columns.address,
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
            orders_all_info.rename(columns=COLUMNS_NAME_TO_COMMON)
            .assign(
                    **{self.common_info_columns.year: lambda d: d[self.common_info_columns.order_date].dt.year},
                    **{self.common_info_columns.month: lambda d: d[self.common_info_columns.order_date].dt.month},
                    **{self.common_info_columns.week: lambda d: d[self.common_info_columns.order_date].dt.isocalendar().week},
                    **{self.common_info_columns.order: None},
                    **{self.common_info_columns.customer_full_name: 'Клиент LAMODA'},
                    **{self.common_info_columns.order_is_canceled: lambda d: d[self.common_info_columns.status].isin(CANCELLED_STATUSES).astype(int)},
                    **{self.common_info_columns.cancel_reason: None},
                    **{self.common_info_columns.doc_sale: None},
                    **{self.common_info_columns.doc_return: None},
                    **{self.common_info_columns.cost_of_delivery: None},
                    **{self.common_info_columns.order_source: 'LAMODA'},
                    **{self.common_info_columns.sender_warehouse: None},
                    **{self.common_info_columns.shop: 'LAMODA'},
                    **{self.common_info_columns.posting_number: None},
                    **{self.common_info_columns.article: lambda d: d[self.orders_info_columns.sku].str.rsplit('_', n=1).str[0]},
                    **{self.common_info_columns.price: lambda d: d[self.common_info_columns.order_sum]},
                    **{self.common_info_columns.quantity: 1},
                    **{self.common_info_columns.sale_sum: lambda d: d[self.common_info_columns.order_sum].where(
                            d[self.common_info_columns.status].isin(['Delivered']), 0)},
                    **{self.common_info_columns.shipping_sum: lambda d: d[self.common_info_columns.order_sum]},
                    **{self.common_info_columns.return_sum: lambda d: d[self.common_info_columns.order_sum].where(
                            d[self.common_info_columns.status].isin(RETURNED_STATUSES), 0)},
                    **{self.common_info_columns.sale_date: lambda d: d[self.orders_info_columns.updated_at].where(
                        d[self.common_info_columns.sale_sum] != 0, None)},
                    **{self.common_info_columns.returned_date: lambda d: d[self.orders_info_columns.updated_at].where(
                        d[self.common_info_columns.return_sum] != 0, None)},
                    **{self.common_info_columns.main_cost_of_return: None},
                    **{self.common_info_columns.main_cost_of_sale: None},
                    **{self.common_info_columns.delivery_method: None},
                    **{self.common_info_columns.project: 'LAMODA'},
                    **{self.common_info_columns.nomenclature_group: None},
                    **{self.common_info_columns.manufacturer_nomenclature_type: lambda d: d[self.common_info_columns.nomenclature].str.split().str[0]},
                    **{self.common_info_columns.manufacturer_nomenclature_product_type: lambda d: d[self.common_info_columns.nomenclature].str.split().str[0]},
                    **{self.common_info_columns.gender: None},
                    **{self.common_info_columns.pickup_point_city: None},
                    **{self.common_info_columns.shop_city: None},
                    **{self.common_info_columns.rrc_sale_sum: None},
                    **{self.common_info_columns.rrc_return_sum: None},
                    **{self.common_info_columns.source: 'LAMODA'},
                    **{self.common_info_columns.seller: None},
                    **{self.common_info_columns.customer_comment: None},
                    **{self.common_info_columns.manager_comment: None},
                    **{self.common_info_columns.email: None},
                    **{self.common_info_columns.phone: None},
                    **{self.common_info_columns.is_paid_on_site: None},
                    **{self.common_info_columns.promo_code: None},
                    **{self.common_info_columns.responsible_shop: None},
                    **{self.common_info_columns.seller_code: None},
                    **{self.common_info_columns.return_invoice_number_1: None},
                    **{self.common_info_columns.return_invoice_number_2: None},
                    **{self.common_info_columns.sale_quantity: lambda d: d[self.common_info_columns.sale_date].notna().astype(int)},
                    **{self.common_info_columns.return_quantity: lambda d: d[self.common_info_columns.returned_date].notna().astype(int)},
                    **{self.common_info_columns.canal: 'LAMODA'},
                    **{self.common_info_columns.returned_sum: lambda d: d[self.common_info_columns.return_sum] + d[self.common_info_columns.order_sum].where(
                        d[self.common_info_columns.order_is_canceled] == 1, 0)}
            )
        )

        common_df = common_df[
            [col for col in asdict(self.common_info_columns).values() if col in common_df.columns]].copy()

        return common_df
