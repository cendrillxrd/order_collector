from wb.workers.clients import WildberriesAPIClient
from wb.strategies.request_strategies import RequestsStrategy


class ContextWbApi:
    def __init__(self, strategy: RequestsStrategy | None = None):
        self._strategy = strategy

    @property
    def strategy(self) -> RequestsStrategy | None:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: RequestsStrategy):
        self._strategy = strategy

    def get_info(self, client: WildberriesAPIClient = WildberriesAPIClient(), *args, **kwargs) -> list[dict]:
        if self._strategy is None:
            raise ValueError('Стратегия не выбрана')
        return self._strategy.do_request(client, *args, **kwargs)