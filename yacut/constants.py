"""Константы для проекта yacut."""

import os

LINK = 2048
SHORT_LINK_MAX = 16
BAD_URL = 'files'
RANDOM_STRING_LENGTH = 6
API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'
DISK_TOKEN = os.getenv('DISK_TOKEN')
AUTH_HEADER = {'Authorization': f'OAuth {DISK_TOKEN}'}
OVERWRITE = True
REQUIRED_KEY = 'url'
OPTIONAL_KEY = 'custom_id'
TO_DICT_SHORT_URL = 'short_link'
CORRECT_SYMBOLS = r'^[a-zA-Z0-9]*$'
