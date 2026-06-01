import pandas as pd

from yandex.strategies.merge_strategies import MergeStrategies


class Merger:
    def __init__(self):
        self.__strategy = None

    def set_strategy(self, strategy: MergeStrategies):
        self.__strategy = strategy

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        merged_df = self.__strategy.merge(df1, df2, *args, **kwargs)
        return merged_df