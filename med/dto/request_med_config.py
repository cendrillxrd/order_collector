from dataclasses import dataclass

from med.med_config import MedUrlKey


@dataclass
class RequestMedConfig:
    url_key: MedUrlKey