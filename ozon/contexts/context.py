from typing import Generic, TypeVar

import pandas as pd

from ozon.workers.clients import OzonAPIClient, HttpClient
from ozon.strategies.convert_strategies import ConvertStrategy
from ozon.strategies.correct_strategies import CorrectStrategy
from ozon.strategies.merge_strategies import MergeStrategy
from ozon.strategies.request_strategies import RequestStrategy

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


class ContextOZONApi(BaseContext[RequestStrategy]):
    def get_info(self, client: OzonAPIClient | None = None, **kwargs) -> list[dict] | str | None:
        if client is None:
            client = OzonAPIClient()
        return self._require_strategy().do_request(client, **kwargs)

class ContextHTTP(BaseContext[RequestStrategy]):
    def get_info(self, client: HttpClient | None = None, **kwargs) -> list[dict] | str | None:
        if client is None:
            client = HttpClient()
        return self._require_strategy().do_request(client, **kwargs)

class ContextOZONCorrect(BaseContext[CorrectStrategy]):
    def correct_info(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return self._require_strategy().do_correct(df, **kwargs)


class ContextOZONMerge(BaseContext[MergeStrategy]):
    def merge_info(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return self._require_strategy().do_merge(df1, df2, **kwargs)


class ContextOZONConvert(BaseContext[ConvertStrategy]):
    def convert_info(self, info: list[dict], **kwargs) -> pd.DataFrame:
        return self._require_strategy().do_convert(info, **kwargs)