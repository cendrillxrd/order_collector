from abc import ABC, abstractmethod
from io import BytesIO

import pandas as pd

from med.dto.med_dto import MedDTO
from med.med_config import BASE_COLLECTIONS_COLUMNS_NAME
from med.utils.corr_helper import correct_columns_name


class ConvertStrategy(ABC):
    def __init__(self) -> None:
        self.collections_columns = MedDTO()
    @abstractmethod
    def do_convert(self, data, **kwargs) -> pd.DataFrame:
        pass

class ConvMEDCollections(ConvertStrategy):
    def do_convert(self, data, **kwargs) -> pd.DataFrame:
        """Преобразует данные о коллекциях на меде в DataFrame"""
        med_collections_df = pd.read_excel(BytesIO(data.content))

        med_collections_df = correct_columns_name(med_collections_df, BASE_COLLECTIONS_COLUMNS_NAME)
        return med_collections_df