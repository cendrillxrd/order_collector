import pandas as pd
from wb.strategies.convert_strategies import ConvertStrategy


class ContextWbConvert:
    def __init__(self, strategy: ConvertStrategy | None = None):
        self._strategy = strategy

    @property
    def strategy(self) -> ConvertStrategy | None:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ConvertStrategy):
        self._strategy = strategy

    def convert_info(self, info: list[dict], *args, **kwargs) -> pd.DataFrame:
        if self._strategy is None:
            raise ValueError('Стратегия не выбрана')
        return self._strategy.do_convert(info, *args, **kwargs)