import pandas as pd

from lamoda.contexts.context import ContextLamodaMerge, ContextLamodaCorrect
from lamoda.strategies.correct_strategies import (
    CorrBrandOrders, CorrOrdersStrategy, CorrReturnsStrategy)
from lamoda.strategies.merge_strategies import (
                                                MergeOrders,
                                                MergeOrdersBrand, MergeOrdersWithReturnsStrategy)


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
        self.merger = ContextLamodaMerge()
        self.corrector = ContextLamodaCorrect()

    @with_strategies(merge_strategy=MergeOrdersBrand, correct_strategy=CorrBrandOrders)
    def merge_orders_with_brand(self, lamoda_df: pd.DataFrame, brand_df: pd.DataFrame) -> pd.DataFrame:
        orders_brand_merged = self.merger.merge_info(lamoda_df, brand_df)
        orders_brand_corrected = self.corrector.correct_info(orders_brand_merged)
        return orders_brand_corrected

    @with_strategies(merge_strategy=MergeOrders)
    def merge_orders_info(self, main_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
        collections_merged = self.merger.merge_info(main_df, new_df)
        return collections_merged

    @with_strategies(correct_strategy=CorrOrdersStrategy)
    def orders_main_info(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        corr_orders = self.corrector.correct_info(orders_df)
        return corr_orders

    @with_strategies(correct_strategy=CorrReturnsStrategy)
    def returns_main_info(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        corr_orders = self.corrector.correct_info(orders_df)
        return corr_orders

    @with_strategies(merge_strategy=MergeOrdersWithReturnsStrategy)
    def merge_main_info(self, orders_df: pd.DataFrame, returns_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge_info(orders_df, returns_df)
        return merged