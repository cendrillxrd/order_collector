from typing import Generic, TypeVar
import pandas as pd

from med.strategies.request_strategies import RequestStrategy
from med.strategies.convert_strategies import ConvertStrategy
from med.strategies.merge_strategies import MergeStrategy
from med.workers.client import MedClient

T = TypeVar('T')

class BaseContext(Generic[T]):
    def __init__(self, strategy: T | None = None):
        self._strategy = strategy

    @property
    def strategy(self) -> T | None:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: T) -> None:
        self._strategy = strategy

    def _require_strategy(self) -> T:
        if self._strategy is None:
            raise ValueError('Стратегия не выбрана')
        return self._strategy

class ContextMedApi(BaseContext[RequestStrategy]):
    def get_info(self, client: MedClient | None = None, **kwargs):
        if client is None:
            client = MedClient()
        return self._require_strategy().do_request(client, **kwargs)

class ContextMedConvert(BaseContext[ConvertStrategy]):
    def convert_info(self, data, **kwargs) -> pd.DataFrame:
        return self._require_strategy().do_convert(data, **kwargs)

class ContextMedMerge(BaseContext[MergeStrategy]):
    def merge_info(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return self._require_strategy().do_merge(df1, df2, **kwargs)