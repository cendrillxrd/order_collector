from typing import Generic, TypeVar, Union

import pandas as pd

from lamoda.strategies.convert_strategies import ConvertStrategy
from lamoda.strategies.correct_strategies import CorrectStrategy
from lamoda.strategies.merge_strategies import MergeStrategy
from lamoda.strategies.request_strategies import RequestStrategy
from lamoda.workers.api_client import APIClient, MedClient

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


class ContextLamodaApi(BaseContext[RequestStrategy]):
    def __init__(self, api_key_manager=None, strategy=None):
        super().__init__(strategy)
        self._api_key_manager = api_key_manager

    def get_info(self, client: APIClient | None = None, **kwargs):
        if client is None:
            client = APIClient(api_key_manager=self._api_key_manager)
        return self._require_strategy().get_info(client, **kwargs)


class ContextMedApi(BaseContext[RequestStrategy]):
    def get_info(self, client: MedClient | None = None, **kwargs):
        if client is None:
            client = MedClient()
        return self._require_strategy().get_info(client, **kwargs)


class ContextLamodaConvert(BaseContext[ConvertStrategy]):
    def convert_info(self, data, **kwargs) -> Union[pd.DataFrame, list]:
        return self._require_strategy().do_convert(data, **kwargs)


class ContextLamodaMerge(BaseContext[MergeStrategy]):
    def merge_info(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return self._require_strategy().merge(df1, df2, **kwargs)


class ContextLamodaCorrect(BaseContext[CorrectStrategy]):
    def correct_info(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return self._require_strategy().do_correct(df, **kwargs)