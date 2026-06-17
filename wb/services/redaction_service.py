import pandas as pd

from wb.context.context_wb_corrector import ContextWbCorrector
from wb.context.context_wb_merge import ContextWbMerge
from wb.strategies.correct_strategies import (CorrOrdersStrategy, CorrSalesStrategy, )
from wb.strategies.merge_strategies import MergeOrdersInfoStrategy, MergeSalesInfoStrategy, MergeOrdersWithSalesStrategy

def with_strategies(merge_strategy=None, corrector_strategy=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if merge_strategy is not None:
                self.merger.strategy = merge_strategy()
            if corrector_strategy is not None:
                self.corrector.strategy = corrector_strategy()
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class RedactionService:
    def __init__(self):
        self.merger = ContextWbMerge()
        self.corrector = ContextWbCorrector()

    @with_strategies(corrector_strategy=CorrOrdersStrategy)
    def get_orders_main_info(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        corr_orders = self.corrector.correct_info(orders_df)
        return corr_orders

    @with_strategies(corrector_strategy=CorrSalesStrategy)
    def get_sales_main_info(self, sales_df: pd.DataFrame) -> pd.DataFrame:
        corr_sales = self.corrector.correct_info(sales_df)
        return corr_sales

    @with_strategies(merge_strategy=MergeOrdersInfoStrategy)
    def merge_orders(self, orders_main_df: pd.DataFrame, new_orders_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge_info(orders_main_df, new_orders_df)
        return merged

    @with_strategies(merge_strategy=MergeSalesInfoStrategy)
    def merge_sales(self, sales_main_df: pd.DataFrame, new_sales_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge_info(sales_main_df, new_sales_df)
        return merged

    @with_strategies(merge_strategy=MergeOrdersWithSalesStrategy)
    def merge_main_info(self, orders_df: pd.DataFrame, sales_df: pd.DataFrame) -> pd.DataFrame:
        merged = self.merger.merge_info(orders_df, sales_df)
        return merged