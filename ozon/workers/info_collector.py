from ozon.dto.info_dto import InfoDTO
from ozon.services.ozon_service import OzonService
from ozon.utils.date_helpers import get_month_ago_iso, get_last_sunday_end_iso, date_month_ago, end_of_last_week


class InfoCollector:
    def __init__(self):
        self.ozon_service = OzonService()

    def collect_info(self) -> InfoDTO:
        cards_info = self.ozon_service.get_cards_info()

        time_from = '2026-06-01T00:00:00+00:00'
        time_to = '2026-06-07T23:59:59+00:00'
        # time_from = date_month_ago() # '2026-04-27T00:00:00+00:00'
        # time_to = end_of_last_week() # '2026-05-03T23:59:59+00:00'

        returns = self.ozon_service.get_returns(time_from, time_to)

        processed_at_from = '2026-06-01T00:00:00Z' # "2026-04-27T00:00:00Z"
        processed_at_to = '2026-06-07T23:59:59Z' # "2026-05-03T23:59:59Z"
        # processed_at_from = get_month_ago_iso() # "2026-04-27T00:00:00Z"
        # processed_at_to = get_last_sunday_end_iso() # "2026-05-03T23:59:59Z"
        orders = self.ozon_service.get_orders(processed_at_from, processed_at_to)

        return InfoDTO(
            cards_info=cards_info,
            orders=orders,
            returns=returns,
        )