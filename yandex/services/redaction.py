import pandas as pd

from yandex.strategies.correct_strategies import CorrOrdersStrategy, CorrReturnsStrategy
from yandex.strategies.merge_strategies import (
    MergeCollections, MergeYandexCollections, MergeOrdersInfoStrategy, MergeReturnsInfoStrategy,
    MergeOrdersWithReturnsStrategy)
from yandex.workers.merger import Merger
from yandex.workers.corrector import Corrector

def with_strategies(merge_strategy_cls=None, correcter_strategy_cls=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if merge_strategy_cls is not None:
                self.merger.set_strategy(merge_strategy_cls())
            if correcter_strategy_cls is not None:
                self.corrector.set_strategy(correcter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator

class RedactionService:
    def __init__(self):
        self.merger = Merger()
        self.corrector = Corrector()

    @with_strategies(merge_strategy_cls=MergeYandexCollections)
    def merge_with_med_collections(self, yandex_df: pd.DataFrame, med_df: pd.DataFrame) -> pd.DataFrame:
        collections_merged = self.merger.merge(yandex_df, med_df)
        return collections_merged

    @with_strategies(merge_strategy_cls=MergeCollections)
    def merge_collections(self, yandex_df: pd.DataFrame, med_df: pd.DataFrame) -> pd.DataFrame:
        collections_merged = self.merger.merge(yandex_df, med_df)
        return collections_merged

    @with_strategies(merge_strategy_cls=MergeOrdersInfoStrategy)
    def merge_orders(self, orders_main_df: pd.DataFrame, new_orders_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge(orders_main_df, new_orders_df)
        return merged

    @with_strategies(correcter_strategy_cls=CorrOrdersStrategy)
    def orders_main_info(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        corr_orders = self.corrector.correct(orders_df)
        return corr_orders

    @with_strategies(merge_strategy_cls=MergeReturnsInfoStrategy)
    def merge_returns(self, returns_main_df: pd.DataFrame, new_returns_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge(returns_main_df, new_returns_df)
        return merged

    @with_strategies(correcter_strategy_cls=CorrReturnsStrategy)
    def returns_main_info(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        corr_orders = self.corrector.correct(orders_df)
        return corr_orders

    @with_strategies(merge_strategy_cls=MergeOrdersWithReturnsStrategy)
    def merge_main_info(self, orders_df: pd.DataFrame, returns_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge(orders_df, returns_df)
        return merged