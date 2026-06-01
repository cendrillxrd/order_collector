import logging

import pandas as pd

from lamoda.strategies.correct_strategies import (
    CorrBrandOrders, CorrOrdersStrategy, CorrReturnsStrategy)
from lamoda.strategies.merge_strategies import (
                                                MergeOrders,
                                                MergeOrdersBrand, MergeOrdersWithReturnsStrategy)
from lamoda.workers.corrector import Corrector
from lamoda.workers.merger import Merger



def with_strategies(merge_strategy_cls: 'CorrectorStrategy' = None,
                    correcter_strategy_cls: 'CorrectorStrategy' = None):
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

    @with_strategies(merge_strategy_cls=MergeOrdersBrand, correcter_strategy_cls=CorrBrandOrders)
    def merge_orders_with_brand(self, lamoda_df: pd.DataFrame, brand_df: pd.DataFrame) -> pd.DataFrame:
        orders_brand_merged = self.merger.merge(lamoda_df, brand_df)
        orders_brand_corrected = self.corrector.correct(orders_brand_merged)
        return orders_brand_corrected

    @with_strategies(merge_strategy_cls=MergeOrders)
    def merge_orders_info(self, main_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
        collections_merged = self.merger.merge(main_df, new_df)
        return collections_merged

    @with_strategies(correcter_strategy_cls=CorrOrdersStrategy)
    def orders_main_info(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        corr_orders = self.corrector.correct(orders_df)
        return corr_orders

    @with_strategies(correcter_strategy_cls=CorrReturnsStrategy)
    def returns_main_info(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        corr_orders = self.corrector.correct(orders_df)
        return corr_orders

    @with_strategies(merge_strategy_cls=MergeOrdersWithReturnsStrategy)
    def merge_main_info(self, orders_df: pd.DataFrame, returns_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge(orders_df, returns_df)
        return merged