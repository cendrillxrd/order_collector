import os
from pathlib import Path

from dotenv import load_dotenv

from lamoda.dto.orders_main_info_dto import OrdersMainInfoColumnsDTO
from lamoda.utils.path_helper import get_desktop_path

load_dotenv()
from lamoda.dto.columns_main_dto import ColumnsMainDTO

columns_main = ColumnsMainDTO()
order_columns_main = OrdersMainInfoColumnsDTO()

BASE_URLS = {
    'live': 'https://api-b2b.lamoda.ru',
    'b2b': 'https://public-api-seller.lamoda.ru',
    'med_collections_1': 'https://med-online.ru/upload/acrit.exportproplus/file.OZON.xlsx?1740656479',
    'med_collections_2': 'https://med-online.ru/upload/acrit.exportproplus/file.OZONdop.xlsx?1744707024',
    'med_collections_3': 'https://med-online.ru/upload/acrit.exportproplus/file.match-bikk.xlsx?1769676747',
    'med_collections_4': 'https://med-online.ru/upload/acrit.exportproplus/file.Strell-Truss-Redp.xlsx?1772624157',
}

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

CLIENT_ID_SMART_PREMIUM = os.getenv('CLIENT_ID_SMART_PREMIUM')
CLIENT_SECRET_SMART_PREMIUM = os.getenv('CLIENT_SECRET_SMART_PREMIUM')

LIMIT_NOMENCLATURE = 25
LIMIT_STOCK = 25
LIMIT_ORDER = 25
TIME_SLEEP_NOMENCLATURES = 0.5
TIME_SLEEP_STOCK = 0.5
TIME_SLEEP_ORDER = 0.5
TIME_SLEEP_ORDER_INFO = 0.2

BASE_COLUMNS_NAME = {'id': columns_main.id,
                     'paymentMethod': columns_main.payment_method,
                     'seller_sku': columns_main.sku,
                     'brand': columns_main.brand,
                     'status': columns_main.status,
                     'sku': columns_main.sku,
                     'status_product': columns_main.status_product,
                     'totalDiscount': columns_main.total_discount,
                     'salePrice': columns_main.sale_price,
                     'paidPrice': columns_main.paid_price,
                     'basePrice': columns_main.base_price,
                     'couponDiscount': columns_main.coupon_discount,
                     'loyaltyDiscount': columns_main.loyalty_discount,
                     'partnerAgreedDiscount': columns_main.partner_agreed_discount,
                     'otherDiscounts': columns_main.other_discounts,
                     'platformDiscounts': columns_main.platform_discounts,
                     'partnerAgreedPrice': columns_main.partner_agreed_price,
                     'city': columns_main.city,
                     'shippingMethodCode': columns_main.shipping_method_code,
                     'shopName': columns_main.shop_name,
                     'size': columns_main.size,
                     'description': columns_main.description,
                     # 'Артикул': columns_main.supplier_parent_sku,
                     }

ON_THE_WAY_SHIP_STATUS = ['Arrived to LME',
                          'Confirmed',
                          'Given to delivery',
                          'In Delivery',
                          'Left LME',
                          'On shelf',
                          'Ready for shipment',
                          'Shipped',
                          'Postponed',
                          'Delivery incidence',
                          'Not delivered',
                          'Not bought',
                          'Rejected',
                          'Delivered',
                          ]

BASE_MAIN_COLUMNS_NAME = {
                     'sum_orders': order_columns_main.sum_orders,
                     'total_orders': order_columns_main.total_orders,
                     'returned': order_columns_main.returned,
                     'returned_sum': order_columns_main.returned_sum,
                     'total_main_orders': order_columns_main.total_main_orders,
}

ON_THE_WAY_GOODS_SHIPS_STATUS = ['Arrived to LM Express',
                                 'Confirmed',
                                 'Given to delivery',
                                 'In delivery',
                                 'Left LM Express',
                                 'On shelf',
                                 'Ready for shipment',
                                 'Shipped',
                                 'Not delivered',
                                 'Not bought',
                                 'Rejected']

DESKTOP_FILE_PATH = get_desktop_path()
LAMODA_FOLDER_NAME = 'LAMODA DATA'
FILE_PATH = os.path.join(DESKTOP_FILE_PATH, LAMODA_FOLDER_NAME)
ORDERS_FILE_NAME = 'Заказы'
NOMENCLATURE_FILE_NAME = 'Номенклатура'
NOMENCLATURE_DAY_FILE_NAME = 'Последняя номенклатура'

DEBUG = os.getenv('DEBUG')
HOME_DIR = Path(__file__).resolve().parent.parent

BASE_ORDERS_FILE_NAME = 'Заказы LAMODA'
BASE_ORDERS_FILE_NAME_SMART_PREMIUM = 'Заказы LAMODA SP'
