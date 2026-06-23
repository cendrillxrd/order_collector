import pandas as pd

from yandex.contexts.context import ContextYandexMerge, ContextYandexCorrect
from yandex.strategies.correct_strategies import CorrOrdersStrategy, CorrReturnsStrategy
from yandex.strategies.merge_strategies import (
    MergeCollections, MergeYandexCollections, MergeOrdersInfoStrategy, MergeReturnsInfoStrategy,
    MergeOrdersWithReturnsStrategy)

def with_strategies(merge_strategy=None, correct_strategy=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if merge_strategy is not None:
                self.merger.strategy = merge_strategy()
            if correct_strategy is not None:
                self.corrector.strategy = correct_strategy()
            return method(self, *args, **kwargs)

        return wrapper

    return decorator

class RedactionService:
    def __init__(self):
        self.merger = ContextYandexMerge()
        self.corrector = ContextYandexCorrect()

    @with_strategies(merge_strategy=MergeYandexCollections)
    def merge_with_med_collections(self, yandex_df: pd.DataFrame, med_df: pd.DataFrame) -> pd.DataFrame:
        collections_merged = self.merger.merge_info(yandex_df, med_df)
        return collections_merged

    @with_strategies(merge_strategy=MergeCollections)
    def merge_collections(self, yandex_df: pd.DataFrame, med_df: pd.DataFrame) -> pd.DataFrame:
        collections_merged = self.merger.merge_info(yandex_df, med_df)
        return collections_merged

    @with_strategies(merge_strategy=MergeOrdersInfoStrategy)
    def merge_orders(self, orders_main_df: pd.DataFrame, new_orders_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge_info(orders_main_df, new_orders_df)
        return merged

    @with_strategies(correct_strategy=CorrOrdersStrategy)
    def orders_main_info(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        corr_orders = self.corrector.correct_info(orders_df)
        return corr_orders

    @with_strategies(merge_strategy=MergeReturnsInfoStrategy)
    def merge_returns(self, returns_main_df: pd.DataFrame, new_returns_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge_info(returns_main_df, new_returns_df)
        return merged

    @with_strategies(correct_strategy=CorrReturnsStrategy)
    def returns_main_info(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        corr_orders = self.corrector.correct_info(orders_df)
        return corr_orders

    @with_strategies(merge_strategy=MergeOrdersWithReturnsStrategy)
    def merge_main_info(self, orders_df: pd.DataFrame, returns_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge_info(orders_df, returns_df)
        return merged