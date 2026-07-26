from enum import StrEnum

from med.dto.med_dto import MedDTO
collections_dto = MedDTO()

BASE_COLLECTIONS_COLUMNS_NAME = {
                     'ID': collections_dto.offer_id,
                    }

class MedUrlKey(StrEnum):
    MED_COLLECTIONS_1 = 'med_collections_1'
    MED_COLLECTIONS_2 = 'med_collections_2'
    MED_COLLECTIONS_3 = 'med_collections_3'
    MED_COLLECTIONS_4 = 'med_collections_4'

MED_BASE_URLS: dict[MedUrlKey, str] = {
    MedUrlKey.MED_COLLECTIONS_1: 'https://med-online.ru/upload/acrit.exportproplus/file.OZON.xlsx?1740656479',
    MedUrlKey.MED_COLLECTIONS_2: 'https://med-online.ru/upload/acrit.exportproplus/file.OZONdop.xlsx?1744707024',
    MedUrlKey.MED_COLLECTIONS_3: 'https://med-online.ru/upload/acrit.exportproplus/file.match-bikk.xlsx?1769676747',
    MedUrlKey.MED_COLLECTIONS_4: 'https://med-online.ru/upload/acrit.exportproplus/file.Strell-Truss-Redp.xlsx?1772624157',
}