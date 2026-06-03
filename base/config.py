from base.dto.all_agg_info_dto import AllAggInfoColumnsDTO

agg_columns = AllAggInfoColumnsDTO()

BASE_MAIN_COLUMNS_NAME = {
                     'sum_orders': agg_columns.sum_orders,
                     'sum_shipment': agg_columns.sum_shipment,
                     'total_orders': agg_columns.total_orders,
                     'returned': agg_columns.returned,
                     'returned_sum': agg_columns.returned_sum,
                     'total_main_orders': agg_columns.total_main_orders,
}

YANDEX_DISC_BASE_FILE_NAME = '/База.xlsx'
LOCAL_PATH = f'.{YANDEX_DISC_BASE_FILE_NAME}'
