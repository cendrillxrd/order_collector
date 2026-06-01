import pandas as pd

from wb.strategies.correct_strategies import (CorrOrdersStrategy, CorrSalesStrategy, )
from wb.strategies.merge_strategies import MergeOrdersInfoStrategy, MergeSalesInfoStrategy, MergeOrdersWithSalesStrategy

from wb.workers.corrector import Corrector
from wb.workers.merger import Merger


# from workers.merger import Merger


def with_strategies(merge_strategy_cls: 'MergeStrategies' = None,
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

    @with_strategies(correcter_strategy_cls=CorrOrdersStrategy)
    def orders_main_info(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        corr_orders = self.corrector.correct(orders_df)
        return corr_orders

    @with_strategies(correcter_strategy_cls=CorrSalesStrategy)
    def sales_main_info(self, sales_df: pd.DataFrame) -> pd.DataFrame:
        corr_sales = self.corrector.correct(sales_df)
        return corr_sales

    @with_strategies(merge_strategy_cls=MergeOrdersInfoStrategy)
    def merge_orders(self, orders_main_df: pd.DataFrame, new_orders_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge(orders_main_df, new_orders_df)
        return merged

    @with_strategies(merge_strategy_cls=MergeSalesInfoStrategy)
    def merge_sales(self, sales_main_df: pd.DataFrame, new_sales_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge(sales_main_df, new_sales_df)
        return merged

    @with_strategies(merge_strategy_cls=MergeOrdersWithSalesStrategy)
    def merge_main_info(self, orders_df: pd.DataFrame, sales_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge(orders_df, sales_df)
        return merged