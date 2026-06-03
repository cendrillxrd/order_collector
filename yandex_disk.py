import yadisk

from config import YANDEX_DISC_API_KEY
from logger import setup_logger

logger = setup_logger("my_app")

def download_file(remote_path: str, local_path: str, token: str = YANDEX_DISC_API_KEY) -> None:
    """
    Скачивает один файл с Яндекс Диска.

    :param remote_path: путь на диске, например "/Выгрузка из базы/База.xlsx"
    :param local_path:  локальный путь, например "./База.xlsx"
    :param token: апи ключ
    """
    client = yadisk.YaDisk(token=token)
    try:
        client.download(remote_path, local_path)
    except yadisk.exceptions.PathNotFoundError:
        logger.info('Файл с данными по проектам не найден')

def upload_file(local_path: str, remote_path: str, token: str = YANDEX_DISC_API_KEY) -> None:
    """
    Загружает один файл на Яндекс Диск.

    :param local_path:  локальный путь к файлу, например "./База.xlsx"
    :param remote_path: путь на диске, например "/Выгрузка из базы/База.xlsx"
    :param token: апи ключ
    """
    client = yadisk.YaDisk(token=token)
    try:
        client.upload(local_path, remote_path, overwrite=True)
    except yadisk.exceptions.PathNotFoundError:
        logger.info('Папка назначения не найдена на Яндекс Диске')
    except FileNotFoundError:
        logger.info('Локальный файл не найден: %s', local_path)
