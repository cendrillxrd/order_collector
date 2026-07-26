import pandas as pd

from logger import setup_logger
from med.med_config import MedUrlKey
from med.contexts.context import ContextMedApi, ContextMedConvert
from med.strategies.request_strategies import ReqMEDCollections
from med.strategies.convert_strategies import ConvMEDCollections

logger = setup_logger("my_app")

class MedService:
    def __init__(self):
        self.med_api_client = ContextMedApi()
        self.converter = ContextMedConvert()

    def get_med_collections(self) -> list[pd.DataFrame]:
        result = []
        for key in MedUrlKey:
            logger.info(f'Получение информации о коллекциях {key}')
            self.med_api_client.strategy = ReqMEDCollections(key)
            self.converter.strategy = ConvMEDCollections()
            data = self.med_api_client.get_info()
            result.append(self.converter.convert_info(data))
        return result