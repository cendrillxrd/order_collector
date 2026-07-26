import pandas as pd

from config import GENERAL_TABLR_PATH, GENERAL_TABLE_FILE_NAME
from wb.workers.info_common_redactor import InfoWBCommonRedactor
from lamoda.workers.info_common_redactor import InfoLamodaCommonRedact
from ozon.workers.info_common_redactor import InfoOZONCommonRedact
from yandex.workers.info_common_redactor import InfoYANDEXCommonRedactor
from base.workers.info_common_redactor import InfoBaseCommonRedact

#WB
info_red = InfoWBCommonRedactor()
wb_com = info_red.redact()

#LAMODA
markets = ['ufo', 'smart_premium']
results = []
for market in markets:
    info_red = InfoLamodaCommonRedact(market)
    info = info_red.redact()
    results.append(info)
lamoda_combined = pd.concat(results)
lamoda_combined.to_excel('lamoda_common.xlsx', index=False)

#OZON
info_red_ozon = InfoOZONCommonRedact()
ozon_com = info_red_ozon.redact()

#YANDEX
info_red_yandex = InfoYANDEXCommonRedactor()
yandex_com = info_red_yandex.redact()

#BASE
info_red_base = InfoBaseCommonRedact()
base_com = info_red_base.redact()

full_com = pd.concat([base_com, wb_com, lamoda_combined, ozon_com, yandex_com])
full_com.to_excel(f'{GENERAL_TABLR_PATH}{GENERAL_TABLE_FILE_NAME}.xlsx', index=False)