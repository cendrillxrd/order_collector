import pandas as pd

from med.contexts.context import ContextMedMerge
from med.strategies.merge_strategies import MergeCollections


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

class RedactionMedService:
    def __init__(self):
        self.merger = ContextMedMerge()

    @with_strategies(merge_strategy=MergeCollections)
    def merge_collections(self, med_df1: pd.DataFrame, med_df2: pd.DataFrame) -> pd.DataFrame:
        collections_merged = self.merger.merge_info(med_df1, med_df2)
        return collections_merged