import os

from dotenv import load_dotenv

from yandex.dto.orders_columns import OrdersColumnsDTO
from yandex.dto.orders_main_info_dto import OrdersMainInfoColumnsDTO
from yandex.dto.returned_columns_dto import ReturnedColumnsDTO

# from yandex.dto.main_columns_dto import YandexColumnsDTO
# from utils.path_helper import get_desktop_path

load_dotenv()
orders_columns = OrdersColumnsDTO()
return_columns = ReturnedColumnsDTO()
order_columns_main = OrdersMainInfoColumnsDTO()


PURCHASE_LOGIN = os.getenv('PURCHASE_LOGIN')
PURCHASE_PASSWORD = os.getenv('PURCHASE_PASSWORD')

API_KEY_YANDEX = os.getenv('YANDEX_API_KEY')

BASE_URLS = {
    'med_collections_1': 'https://med-online.ru/upload/acrit.exportproplus/file.OZON.xlsx?1740656479',
    'med_collections_2': 'https://med-online.ru/upload/acrit.exportproplus/file.OZONdop.xlsx?1744707024',
    'med_collections_3': 'https://med-online.ru/upload/acrit.exportproplus/file.match-bikk.xlsx?1769676747',
    'med_collections_4': 'https://med-online.ru/upload/acrit.exportproplus/file.Strell-Truss-Redp.xlsx?1772624157',
    'med_purchase': 'https://med-online.ru/upload/1cdata/cost.csv',
    'med_prices': 'https://med-online.ru/upload/acrit.exportproplus/file.prices.csv?1755164681',
    'http': '',
    'yandex': 'https://api.partner.market.yandex.ru',
}

BASE_ORDERS_COLUMNS_NAME = {
                     'orderId': orders_columns.order_id,
                     'campaignId': orders_columns.campaign_id,
                     'programType': orders_columns.program_type,
                     'externalOrderId': orders_columns.external_order_id,
                     'status': orders_columns.status,
                     'substatus': orders_columns.substatus,
                     'creationDate': orders_columns.creation_date,
                     'updateDate': orders_columns.update_date,
                     'paymentType': orders_columns.payment_type,
                     'paymentMethod': orders_columns.payment_method,
                     'fake': orders_columns.fake,
                     'notes': orders_columns.notes,
                     'offer_id': orders_columns.offer_id,
                     'offer_name': orders_columns.name,
                     'count': orders_columns.count,
                     'prices.payment.value': orders_columns.price,
                    }

BASE_RETURNS_COLUMNS_NAME = {
                     'orderId': return_columns.order_id,
                     'creationDate': return_columns.creation_date,
                     'updateDate': return_columns.update_date,
                     'shopSku': return_columns.offer_id,
                     'amount.value': return_columns.amount,
                     'count': return_columns.count,
                     'refundStatus': return_columns.refundStatus,
                     'comment': return_columns.comment,
                    }

BASE_MAIN_COLUMNS_NAME = {
                     'sum_orders': order_columns_main.sum_orders,
                     'sum_shipment': order_columns_main.sum_shipment,
                     'total_orders': order_columns_main.total_orders,
                     'returned': order_columns_main.returned,
                     'returned_sum': order_columns_main.returned_sum,
                     'total_main_orders': order_columns_main.total_main_orders,
}

BASE_COLLECTIONS_COLUMNS_NAME = {
                     'ID': orders_columns.offer_id,
                    }

BASE_ORDERS_FILE_NAME = 'Заказы YANDEX'
BASE_RETURNS_FILE_NAME = 'Возвраты YANDEX'


LIMIT_CARDS_INFO = 100
TIME_SLEEP_CARDS_INFO = 0.1

LIMIT_PUBLISHED_CARDS = 200
TIME_SLEEP_PUBLISHED_CARDS = 0.1

LIMIT_ORDERS = 50
TIME_SLEEP_ORDERS = 0.1

LIMIT_RETURNS = 50

TIME_SLEEP_REPORT = 30

SEX_ATTRIBUTE_ID=14805991

FUNNEL_FILE_NAME = 'Воронка YANDEX.csv'
STOCKS_FILE_NAME = 'Остатки YANDEX.csv'

# DESKTOP_FILE_PATH = get_desktop_path()
YANDEX_FOLDER_NAME = 'YANDEX'

NEED_UPDATE = False