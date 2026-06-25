import pandas as pd

from lamoda.strategies.correct_strategies import CorrectStrategy


class Corrector:
    def __init__(self):
        self.__strategy = None

    def set_strategy(self, strategy: CorrectStrategy):
        self.__strategy = strategy

    def correct(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.correcting(df)
