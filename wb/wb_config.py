import os
from enum import StrEnum
from dotenv import load_dotenv

from wb.dto.orders_columns_dto import OrdersColumnsDTO
from wb.dto.sales_columns_dto import SalesColumnsDTO
from wb.dto.orders_main_info_dto import OrdersMainInfoColumnsDTO

load_dotenv()
order_columns = OrdersColumnsDTO()
sales_columns = SalesColumnsDTO()
order_columns_main = OrdersMainInfoColumnsDTO()

class ApiType(StrEnum):
    CONTENT = 'Content_Marketplace_API_KEY'
    STATISTICS = 'Statistics_API_KEY'
    PRICES = 'Price_discount_API_KEY'

API_KEYS: dict[ApiType, str | None] = {
    ApiType.CONTENT: os.getenv('CONTENT_MARKETPLACE_API_KEY'),
    ApiType.STATISTICS: os.getenv('ANALYTICS_STATISTICS_API_KEY'),
    ApiType.PRICES: os.getenv('PRICE_DISCOUNT_API_KEY'),
}

class UrlKey(StrEnum):
    STATISTICS = 'statistics'

BASE_URLS: dict[UrlKey, str] = {
    UrlKey.STATISTICS: 'https://statistics-api.wildberries.ru',
}

BASE_MAIN_COLUMNS_NAME = {
                     'sum_orders': order_columns_main.sum_orders,
                     'sum_shipment': order_columns_main.sum_shipment,
                     'total_orders': order_columns_main.total_orders,
                     'returned': order_columns_main.returned,
                     'returned_sum': order_columns_main.returned_sum,
                     'total_main_orders': order_columns_main.total_main_orders,

}

BASE_COLUMNS_ORDERS_NAME = {
                     'date': order_columns.date,
                     'nmId': order_columns.nmId,
                     'lastChangeDate': order_columns.lastChangeDate,
                     'brand': order_columns.brand,
                     'warehouseName': order_columns.warehouseName,
                     'supplierArticle':  order_columns.supplierArticle,
                     'barcode': order_columns.barcode,
                     'category': order_columns.category,
                     'subject': order_columns.subject,
                     'techSize': order_columns.techSize,
                     'incomeID': order_columns.incomeID,
                     'totalPrice': order_columns.totalPrice,
                     'discountPercent': order_columns.discountPercent,
                     'gNumber': order_columns.gNumber,
                     'sticker':order_columns.sticker,
                     'srid': order_columns.srid,
                     'isCancel': order_columns.isCanceled,
                     }

BASE_COLUMNS_SALES_NAME = {
                     'date': sales_columns.date,
                     'nmId': sales_columns.nmId,
                     'lastChangeDate': sales_columns.lastChangeDate,
                     'brand': sales_columns.brand,
                     'warehouseName': sales_columns.warehouseName,
                     'countryName': sales_columns.countryName,
                     'oblastOkrugName': sales_columns.oblastOkrugName,
                     'regionName': sales_columns.regionName,
                     'supplierArticle':  sales_columns.supplierArticle,
                     'barcode': sales_columns.barcode,
                     'category': sales_columns.category,
                     'subject': sales_columns.subject,
                     'techSize': sales_columns.techSize,
                     'incomeID': sales_columns.incomeID,
                     'totalPrice': sales_columns.totalPrice,
                     'gNumber': sales_columns.gNumber,
                     'sticker':sales_columns.sticker,
                     'srid': sales_columns.srid,
                     'spp': sales_columns.spp,
                     'forPay': sales_columns.forPay,
                     'finishedPrice': sales_columns.finishedPrice,
                     'discountPercent': sales_columns.discountPercent,
                     'priceWithDisc': sales_columns.priceWithDisc,
                     'saleID': sales_columns.saleID,
                     }

TIME_SLEEP_ORDERS = 60  # >= 60
TIME_SLEEP_SALES = 60  # >= 60
RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)
MAX_WAIT_SECONDS = 10

MARKET_NAME = 'WB'

YANDEX_DISC_SALES_FILE_NAME = '/Продажи WB.xlsx'
YANDEX_DISC_ORDERS_FILE_NAME = '/Заказы WB.xlsx'
LOCAL_SALES_PATH = f'.{YANDEX_DISC_SALES_FILE_NAME}'
LOCAL_ORDERS_PATH = f'.{YANDEX_DISC_ORDERS_FILE_NAME}'
