from base.workers.info_collector import InfoCollector
from base.workers.info_redactor import InfoRedactor


def base_main():
    info_collector = InfoCollector()
    info = info_collector.collect_info()

    info_redactor = InfoRedactor()
    info_redacted = info_redactor.redact_info(info)

    return info_redacted
