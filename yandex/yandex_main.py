from yandex.dto.info_yandex_dto import InfoYandexDTO
from yandex.workers.info_collector import InfoCollector
from yandex.workers.info_redactor import InfoRedactor


# from yandex.workers.info_redactor import InfoRedactor


def yandex_main(get_new_info:bool =False):
    if get_new_info:
        info_collector = InfoCollector()
        info = info_collector.collect_info()

        info_redactor = InfoRedactor()
        info_redacted = info_redactor.redact_info(info, get_new_info)

        return info_redacted
    else:
        info_redactor = InfoRedactor()
        info_redacted = info_redactor.redact_info(InfoYandexDTO(), get_new_info)

        return info_redacted