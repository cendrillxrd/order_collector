import os
from pathlib import Path
from dotenv import load_dotenv
from ozon.dto.orders_columns_dto import OrdersColumnsDTO
from ozon.dto.orders_main_info_dto import OrdersMainInfoColumnsDTO
from ozon.dto.returns_columns_dto import ReturnsColumnsDTO
from yandex.config import TIME_SLEEP_REPORT, return_columns

order_columns_dto = OrdersColumnsDTO()
order_main_columns_dto = OrdersMainInfoColumnsDTO()
return_columns_dto = ReturnsColumnsDTO()

# from dto.columns_dto import MainColumnsDTO
# main_columns_dto = MainColumnsDTO()

load_dotenv()

DEBUG = os.getenv('DEBUG')
HOME_DIR = Path(__file__).resolve().parent.parent

API_KEY = os.getenv('OZON_API_KEY')
CLIENT_ID = os.getenv('OZON_CLIENT_ID')

BASE_URLS = {
    'ozon': 'https://api-seller.ozon.ru',
    'med_collections_1': 'https://med-online.ru/upload/acrit.exportproplus/file.OZON.xlsx?1740656479',
    'med_collections_2': 'https://med-online.ru/upload/acrit.exportproplus/file.OZONdop.xlsx?1744707024',
    'med_collections_3': 'https://med-online.ru/upload/acrit.exportproplus/file.match-bikk.xlsx?1769676747',
    'med_collections_4': 'https://med-online.ru/upload/acrit.exportproplus/file.Strell-Truss-Redp.xlsx?1772624157',
    'http': '',
}

BASE_COLUMNS_NAME = {'ID': order_columns_dto.offer_id,
                     'sum_orders': order_main_columns_dto.sum_orders,
                     'sum_shipment': order_main_columns_dto.sum_shipment,
                     'total_orders': order_main_columns_dto.total_orders,
                     'returned': order_main_columns_dto.returned,
                     'returned_sum': order_main_columns_dto.returned_sum,
                     'total_main_orders': order_main_columns_dto.total_main_orders,
                   }

BASE_RETURNS_COLUMNS_NAME = {'id': return_columns_dto.id,
                             'order_number': return_columns_dto.order_number,
                             'posting_number': return_columns_dto.posting_number,
                             'return_date': return_columns_dto.return_date,
                             'return_reason_name': return_columns_dto.return_reason_name,
                             'type': return_columns_dto.type,
                             'schema': return_columns_dto.schema,
                             'sku': return_columns_dto.sku,
                             'offer_id': return_columns_dto.offer_id,
                             'name': return_columns_dto.name,
                             'price.price': return_columns_dto.price,
                             'quantity': return_columns_dto.quantity,
                   }

BASE_RETURNS_STATUSES = ['PartialReturn', 'ClientReturn']

ORDER_STATUSES = ['Ожидает в ПВЗ', 'Доставляется', 'Ожидает сборки', 'Ожидает отгрузки']

LIMIT_RETURNS = 500
TIME_SLEEP_RETURNS = 5

LIMIT_FUNNEL = 1000
LIMIT_ATTRIBUTES = 1000
TIME_SLEEP_FUNNEL = 60
TIME_SLEEP_REPORT = 60
TIME_SLEEP_CARDS_LINK = 30
TIME_SLEEP_ATTRIBUTES_LINK = 30
TIME_SLEEP_STOCKS_FBS = 0.5

SEX_ATTRIBUTE_ID = 9163

FILE_PATH = 'C:/Users/Admin/Desktop/'

YANDEX_DISC_RETURNS_FILE_NAME = '/Возвраты OZON.xlsx'
YANDEX_DISC_ORDERS_FILE_NAME = '/Заказы OZON.xlsx'
LOCAL_RETURNS_PATH = f'.{YANDEX_DISC_RETURNS_FILE_NAME}'
LOCAL_ORDERS_PATH = f'.{YANDEX_DISC_ORDERS_FILE_NAME}'