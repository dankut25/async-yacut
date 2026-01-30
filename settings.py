"""Конфигурация создания приложения."""

import os
from dotenv import load_dotenv


load_dotenv()


class Config(object):
    """Задание настроект для Flask."""

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_value')
