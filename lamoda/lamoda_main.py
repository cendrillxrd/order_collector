import pandas as pd

from lamoda.dto.info_dto import InfoDTO
from lamoda.workers.info_collector import InfoCollector
from lamoda.workers.info_redactor import InfoRedactor


def lamoda_main(get_new_info: bool = False):
    if get_new_info:
        markets = ['ufo', 'smart_premium']
        results = []
        for market in markets:
            info_collector = InfoCollector(market)
            info = info_collector.collect_info()

            info_redactor = InfoRedactor(market)
            result = info_redactor.redact_info(info, get_new_info)
            results.append(result)

        combined = pd.concat(results)
        return combined
    else:
        markets = ['ufo', 'smart_premium']
        results = []
        for market in markets:
            info_redactor = InfoRedactor(market)
            result = info_redactor.redact_info(InfoDTO(), get_new_info)
            results.append(result)

        combined = pd.concat(results)
        return combined
