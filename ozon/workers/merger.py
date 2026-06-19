import pandas as pd

from ozon.strategies.merge_strategies import MergeStrategy


class Merger:
    def __init__(self):
        self.__strategy = None

    def set_strategy(self, strategy: MergeStrategy):
        self.__strategy = strategy

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame, *args) -> pd.DataFrame:
        merged_df = self.__strategy.merge(df1, df2, *args)
        return merged_df