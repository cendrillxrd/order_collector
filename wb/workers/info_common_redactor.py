import pandas as pd
import re

from columns_common_dto import ColumnsCommonDTO, asdict
from wb.dto.orders_columns_dto import OrdersColumnsDTO
from wb.dto.sales_columns_dto import SalesColumnsDTO
from wb.repositories.db_repository import read_orders, read_sales


class InfoWBCommonRedactor:
    def __init__(self):
        self.sales_all_info_columns = SalesColumnsDTO()
        self.orders_all_info_columns = OrdersColumnsDTO()
        self.common_info_columns = ColumnsCommonDTO()

    def redact(self):
        #Обновления бд нет, работаю уже с готовыми данными
        orders_all_info = read_orders()
        sales_all_info = read_sales()

        #Делаю две таблицы (продажи и возвраты) и оставляю только id и дату
        only_sales = sales_all_info[sales_all_info[self.sales_all_info_columns.saleID].astype(str).str.startswith('S', na=False)].copy()
        only_sales = only_sales[[self.sales_all_info_columns.srid, self.sales_all_info_columns.date]]

        only_returns = sales_all_info[sales_all_info[self.sales_all_info_columns.saleID].astype(str).str.startswith('R', na=False)].copy()
        only_returns = only_returns[[self.sales_all_info_columns.srid, self.sales_all_info_columns.date]]
        COLUMN_DATE_RETURN = 'Дата возврата'
        only_returns.rename({self.sales_all_info_columns.date: COLUMN_DATE_RETURN}, axis=1, inplace=True)

        #Объединяю данные
        orders_sales = pd.merge(orders_all_info, only_sales, on=self.sales_all_info_columns.srid, how='left')
        ordered_sales_returns = pd.merge(orders_sales, only_returns, on=self.sales_all_info_columns.srid, how='left')

        def strip_last_two_segments(value: str) -> str:
            return re.sub(r'\.[^.]+\.[^.]+$', '', str(value))

        #Обработка id заказа
        ordered_sales_returns[self.orders_all_info_columns.srid] = ordered_sales_returns[self.orders_all_info_columns.srid].apply(strip_last_two_segments)

        COLUMNS_NAME_TO_COMMON = {
            self.orders_all_info_columns.srid: self.common_info_columns.order_id,
            #order
            self.orders_all_info_columns.date: self.common_info_columns.order_date,
            #customer_full_name
            self.orders_all_info_columns.isCanceled: self.common_info_columns.order_is_canceled,
            #cancel_reason
            #doc_sale
            #doc_return
            #status
            self.orders_all_info_columns.price_with_discount: self.common_info_columns.order_sum,
            #cost_of_delivery
            #order_source
            self.orders_all_info_columns.warehouseName: self.common_info_columns.sender_warehouse,
            #shop
            #posting_number
            #nomenclature
            self.orders_all_info_columns.supplierArticle: self.common_info_columns.article,
            self.orders_all_info_columns.techSize: self.common_info_columns.characteristic_nomenclature,
            self.orders_all_info_columns.brand: self.common_info_columns.manufacturer,
            #price
            #quantity
            #sale_sum
            #return_sum
            self.sales_all_info_columns.date: self.common_info_columns.sale_date,
            COLUMN_DATE_RETURN: self.common_info_columns.returned_date,
            #main_cost_of_return
            #main_cost_of_sale
            #delivery_method
            #project
            self.orders_all_info_columns.category: self.common_info_columns.nomenclature_group,
            self.orders_all_info_columns.subject: self.common_info_columns.manufacturer_nomenclature_type,
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
            ordered_sales_returns.rename(columns=COLUMNS_NAME_TO_COMMON)
            .assign(
                    **{self.common_info_columns.year: lambda d: d[self.common_info_columns.order_date].dt.year},
                    **{self.common_info_columns.month: lambda d: d[self.common_info_columns.order_date].dt.month},
                    **{self.common_info_columns.week: lambda d: d[self.common_info_columns.order_date].dt.isocalendar().week},
                    **{self.common_info_columns.order: None},
                    **{self.common_info_columns.customer_full_name: 'Клиент WB'},
                    **{self.common_info_columns.cancel_reason: None},
                    **{self.common_info_columns.doc_sale: None},
                    **{self.common_info_columns.doc_return: None},
                    **{self.common_info_columns.status: None},
                    **{self.common_info_columns.cost_of_delivery: None},
                    **{self.common_info_columns.order_source: 'WB'},
                    **{self.common_info_columns.shop: 'WB'},
                    **{self.common_info_columns.posting_number: None},
                    **{self.common_info_columns.nomenclature: None},
                    **{self.common_info_columns.price: lambda d: d[self.common_info_columns.order_sum]},
                    **{self.common_info_columns.quantity: 1},
                    **{self.common_info_columns.shipping_sum: lambda d: d[self.common_info_columns.order_sum]},
                    **{self.common_info_columns.sale_sum: lambda d: d[self.common_info_columns.order_sum].where(
                            d[self.common_info_columns.sale_date].notna(), 0)},
                    **{self.common_info_columns.return_sum: lambda d: d[self.common_info_columns.order_sum].where(
                        d[self.common_info_columns.returned_date].notna(), 0)},
                    **{self.common_info_columns.main_cost_of_return: None},
                    **{self.common_info_columns.main_cost_of_sale: None},
                    **{self.common_info_columns.delivery_method: None},
                    **{self.common_info_columns.project: 'WB'},
                    **{self.common_info_columns.manufacturer_nomenclature_product_type: lambda d: d[self.common_info_columns.manufacturer_nomenclature_type]},
                    **{self.common_info_columns.gender: None},
                    **{self.common_info_columns.pickup_point_city: None},
                    **{self.common_info_columns.shop_city: None},
                    **{self.common_info_columns.rrc_sale_sum: None},
                    **{self.common_info_columns.rrc_return_sum: None},
                    **{self.common_info_columns.source: 'WB'},
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
                    **{self.common_info_columns.sale_quantity: lambda d: d[self.common_info_columns.sale_date].notna().astype(int)},
                    **{self.common_info_columns.return_quantity: lambda d: d[self.common_info_columns.returned_date].notna().astype(int)},
                    **{self.common_info_columns.canal: 'WB'},
                    **{self.common_info_columns.returned_sum: lambda d: d[self.common_info_columns.return_sum] + d[self.common_info_columns.order_sum].where(
                            d[self.common_info_columns.order_is_canceled] == 1, 0)}
            )
        )

        common_df = common_df[
            [col for col in asdict(self.common_info_columns).values() if col in common_df.columns]].copy()

        common_df.to_excel('wb_common.xlsx', index=False)
        return common_df
