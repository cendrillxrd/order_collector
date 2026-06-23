from typing import Generic, TypeVar
import pandas as pd

from yandex.strategies.requests_strategies import RequestStrategy
from yandex.strategies.convert_strategies import ConvertStrategy
from yandex.strategies.merge_strategies import MergeStrategy
from yandex.strategies.correct_strategies import CorrectStrategy
from yandex.workers.client import YandexAPIClient, MedClient

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


class ContextYandexApi(BaseContext[RequestStrategy]):
    def get_info(self, client: YandexAPIClient | None = None, **kwargs):
        if client is None:
            client = YandexAPIClient()
        return self._require_strategy().do_request(client, **kwargs)


class ContextMedApi(BaseContext[RequestStrategy]):
    def get_info(self, client: MedClient | None = None, **kwargs):
        if client is None:
            client = MedClient()
        return self._require_strategy().do_request(client, **kwargs)


class ContextYandexConvert(BaseContext[ConvertStrategy]):
    def convert_info(self, data, **kwargs) -> pd.DataFrame:
        return self._require_strategy().do_convert(data, **kwargs)


class ContextYandexMerge(BaseContext[MergeStrategy]):
    def merge_info(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return self._require_strategy().do_merge(df1, df2, **kwargs)


class ContextYandexCorrect(BaseContext[CorrectStrategy]):
    def correct_info(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return self._require_strategy().do_correct(df, **kwargs)