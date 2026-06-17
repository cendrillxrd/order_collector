import pandas as pd

from wb.strategies.correct_strategies import CorrectStrategy


class ContextWbCorrector:
    def __init__(self, strategy: CorrectStrategy | None = None):
        self._strategy = strategy

    @property
    def strategy(self) -> CorrectStrategy | None:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: CorrectStrategy):
        self._strategy = strategy

    def correct_info(self, df1: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        if self._strategy is None:
            raise ValueError('Стратегия не выбрана')
        return self._strategy.do_correct(df1, *args, **kwargs)