from ozon.dto.info_dto import InfoDTO
from ozon.workers.info_collector import InfoCollector
from ozon.workers.info_redactor import InfoRedactor


def ozon_main(get_new_info: bool = False):
    if get_new_info:
        info_collector = InfoCollector()
        info = info_collector.collect_info()

        info_redactor = InfoRedactor()
        info_redacted = info_redactor.redact_info(info, get_new_info)

        return info_redacted
    else:
        info_redactor = InfoRedactor()
        info_redacted = info_redactor.redact_info(InfoDTO(), get_new_info)

        return info_redacted