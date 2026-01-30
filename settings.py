"""Конфигурация создания приложения."""

import os


class Config(object):
    """Задание настроект для Flask."""

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
