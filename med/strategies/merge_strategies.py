from abc import ABC, abstractmethod

import pandas as pd

class MergeStrategy(ABC):
    @abstractmethod
    def do_merge(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        pass

class MergeCollections(MergeStrategy):
    def do_merge(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        merged_df = pd.concat([df1, df2], ignore_index=True)
        return merged_df