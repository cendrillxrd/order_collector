import logging

import pandas as pd

from ozon.contexts.context import ContextOZONCorrect
from ozon.contexts.context import ContextOZONMerge
from ozon.strategies.correct_strategies import CorrOrdersStrategy, CorrReturnsStrategy
from ozon.strategies.merge_strategies import MergeWithBrandStrategy, \
    MergeOrdersInfoStrategy, MergeReturnsInfoStrategy, MergeOrdersWithReturnsStrategy



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
        self.merger = ContextOZONMerge()
        self.corrector = ContextOZONCorrect()

    @with_strategies(merge_strategy=MergeWithBrandStrategy)
    def merge_with_brand(self, main_df: pd.DataFrame, brand_df: pd.DataFrame) -> pd.DataFrame:
        with_brand_merged = self.merger.merge_info(main_df, brand_df)
        return with_brand_merged

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