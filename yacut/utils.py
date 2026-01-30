"""Вспомогательные функции для реализации работы yacut."""

import aiohttp
import asyncio
import random
import re
import string
import urllib.parse

from aiohttp import ClientSession
from typing import Dict, List
from werkzeug.datastructures import FileStorage

from . import db
from .constants import (
    AUTH_HEADER,
    BAD_URL,
    CORRECT_SYMBOLS,
    DOWNLOAD_LINK_URL,
    OPTIONAL_KEY,
    OVERWRITE,
    RANDOM_STRING_LENGTH,
    REQUEST_UPLOAD_URL,
    REQUIRED_KEY
)
from .error_handlers import (
    AsyncGetDownloadURLError,
    AsyncGetUploadURLError,
    AsyncUploadFileError,
    ErrorInDBSave,
    ErrorInURLNaming,
    InvalidAPIUsage
)
from .models import URLMap


db_semaphore = asyncio.Semaphore(1)


def validate_short_url(url: str) -> bool:
    """Валидация введенной пользователем короткой ссылки."""
    start = url.startswith(BAD_URL)
    length = (len(url) == len(BAD_URL))
    check = (URLMap.query.filter_by(short=url).first() is not None)
    return False if (start and length) or check else True


def generate_short_id() -> str:
    """Создание случайной короткой ссылки с проверкой по базе."""
    symbols = string.ascii_letters + string.digits
    while True:
        url = ''.join(random.choices(symbols, k=RANDOM_STRING_LENGTH))
        if URLMap.query.filter_by(short=url).first() is not None:
            continue
        return url


def get_unique_short_id(full_url: str, short_url: str = '') -> str:
    """Проверка и возврат сохраненной короткой ссылки.

    Принимает на вход данные из полей формы: исходная ссылка и вариант
    короткой, если есть.
    Если короткая ссылка не задана, то возвращает созданное уникальное
    короткое имя в виде ссылки для вызова на текущем сервере.
    Если короткая ссылка задана, то валидирует. При успешной валидации
    возвращает ту же строку, в противном случае выбрасывает ошибку.
    В случае успешного создания ссылки, запись: длинная ссылка + короткая
    - сохраняются в базе.
    """
    if not short_url:
        short_url = generate_short_id()
    if not validate_short_url(short_url):
        raise ErrorInURLNaming
    try:
        new_link = URLMap(original=full_url, short=short_url)
        db.session.add(new_link)
        db.session.commit()
        return short_url
    except Exception:
        db.session.rollback()
        raise ErrorInDBSave


async def get_upload_url(session: ClientSession, file: FileStorage) -> str:
    """Получение ссылки на загрузку файла."""
    payload = {
        'path': 'app:/' + urllib.parse.quote(file.filename),
        'overwrite': f'{OVERWRITE}'
    }
    try:
        async with session.get(
            headers=AUTH_HEADER,
            params=payload,
            url=REQUEST_UPLOAD_URL
        ) as response:
            data = await response.json()
            upload_url = data['href']
    except Exception:
        raise AsyncGetUploadURLError
    return upload_url


async def upload_file(
        session: ClientSession, upload_url: str, file: FileStorage
) -> str:
    """Загрузка файла на ЯндексДиск.

    Возвращает короткий путь к файлу на ЯндексДиске.
    """
    try:
        async with session.put(data=file.stream, url=upload_url, ) as response:
            location = response.headers['Location']
            location = urllib.parse.unquote(location)
            location = location.replace('/disk', '')
    except Exception:
        raise AsyncUploadFileError
    return location


async def get_download_url(session: ClientSession, location: str) -> str:
    """Получение ссылки на загрузку файла по короткому пути на ЯндексДиске."""
    try:
        async with session.get(
            headers=AUTH_HEADER,
            url=DOWNLOAD_LINK_URL,
            params={'path': f'{location}'}
        ) as response:
            data = await response.json()
            link = data['href']
    except Exception:
        raise AsyncGetDownloadURLError
    return link


async def upload_file_and_get_url(
        session: ClientSession, file: FileStorage, host_url: str
) -> Dict[str, str]:
    """Загрузка одного файла на ЯндексДиск и получение ссылки на скачивание.

    Принимает на вход текущую сессию aiohttp и файл, который нужно загрузить.
    Возвращает словарь из имени файла, короткой ссылки на него.
    """
    try:
        upload_url = await get_upload_url(session, file)
        location = await upload_file(session, upload_url, file)
        link = await get_download_url(session, location)
        # Добавлена регулировка потоков записи в базу, так как переодически
        # наблюдались ошибки в БД из параллельных обращений.
        async with db_semaphore:
            url = await asyncio.to_thread(get_unique_short_id, link)
        return {
            'name': file.filename,
            'url': f"{host_url.rstrip('/')}/{url.lstrip('/')}",
            'error': ''
        }
    except AsyncGetUploadURLError:
        message = 'Не удалось получить ссылку для загрузки на диск.'
    except AsyncUploadFileError:
        message = 'Не удалось загрузить файл на диск'
    except AsyncGetDownloadURLError:
        message = 'Не удалось получить ссылку для скачивания.'
    except ErrorInDBSave:
        message = 'Не удалось создать запись в БД.'
    except Exception as e:
        message = f'Непредвиденная ошибка: {str(e)}'
    return {'name': file.filename, 'url': 'http://localhost', 'error': message}


async def async_upload_files_to_yadisc(
        files: List[FileStorage], host_url: str
) -> List[Dict[str, str]]:
    """Управление загрузкой присланных файлов на ЯндексДиск.

    Возвращает список из словарей загруженных файлов:
    имя файла, короткая ссылка, ошибка, если была.
    """
    if not files:
        return []

    async with aiohttp.ClientSession() as session:
        tasks = list(
            upload_file_and_get_url(session, file, host_url) for file in files
        )
        uploaded_files = await asyncio.gather(*tasks)
    return uploaded_files


def validate_api_data(data: Dict):
    """Валидация данных, принятых через API по '/api/id/'."""
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')

    if REQUIRED_KEY not in data:
        raise InvalidAPIUsage('\"url\" является обязательным полем!')

    if OPTIONAL_KEY in data:
        short_url = data[OPTIONAL_KEY]

        if not isinstance(short_url, str):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )

        length = len(short_url) <= 16
        symbols = re.match(CORRECT_SYMBOLS, short_url)

        if not (length and symbols):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
