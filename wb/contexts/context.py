from typing import Generic, TypeVar

import pandas as pd

from wb.strategies.convert_strategies import ConvertStrategy
from wb.strategies.correct_strategies import CorrectStrategy
from wb.strategies.merge_strategies import MergeStrategy
from wb.strategies.request_strategies import RequestStrategy
from wb.workers.clients import WildberriesAPIClient

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


class ContextWbApi(BaseContext[RequestStrategy]):
    def get_info(self, client: WildberriesAPIClient | None = None, **kwargs) -> list[dict]:
        if client is None:
            client = WildberriesAPIClient()
        return self._require_strategy().do_request(client, **kwargs)


class ContextWbCorrect(BaseContext[CorrectStrategy]):
    def correct_info(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return self._require_strategy().do_correct(df, **kwargs)


class ContextWbMerge(BaseContext[MergeStrategy]):
    def merge_info(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return self._require_strategy().do_merge(df1, df2, **kwargs)


class ContextWbConvert(BaseContext[ConvertStrategy]):
    def convert_info(self, info: list[dict], **kwargs) -> pd.DataFrame:
        return self._require_strategy().do_convert(info, **kwargs)