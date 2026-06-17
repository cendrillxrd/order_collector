import pandas as pd

from wb.strategies.merge_strategies import MergeStrategy


class ContextWbMerge:
    def __init__(self, strategy: MergeStrategy | None = None):
        self._strategy = strategy

    @property
    def strategy(self) -> MergeStrategy | None:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: MergeStrategy):
        self._strategy = strategy

    def merge_info(self, df1: pd.DataFrame, df2: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        if self._strategy is None:
            raise ValueError('Стратегия не выбрана')
        return self._strategy.do_merge(df1, df2, *args, **kwargs)