from logger import setup_logger
from yandex.dto.info_yandex_dto import InfoYandexDTO
from med.services.med_service import MedService
from yandex.services.yandex_service import YandexService
from yandex.utils.date_helper import get_date_30_days_before_last_week_end, get_last_week_sunday

logger = setup_logger("my_app")


class InfoCollector:
    def __init__(self):
        self.yandex = YandexService()
        self.med = MedService()

    def collect_info(self) -> InfoYandexDTO:
        # date_from, date_to = '2026-06-01','2026-06-07'
        date_from = get_date_30_days_before_last_week_end()
        date_to = get_last_week_sunday()

        returns = self.yandex.get_returns(date_from=date_from, date_to=date_to)
        orders = self.yandex.get_orders()
        med_collections = self.med.get_med_collections()

        return InfoYandexDTO(
            orders=orders,
            returns=returns,
            med_collections=med_collections
        )