"""Перехват ошибок в проекте."""

from flask import jsonify, render_template
from http import HTTPStatus

from . import app, db


@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_error(error):
    """Ошибка 500 для HTML-страниц проекта."""
    db.session.rollback()
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error):
    """Ошибка 404 для HTML-страниц проекта."""
    return render_template('404.html'), HTTPStatus.NOT_FOUND


class YaCutErrors(Exception):
    """Базовый класс для перехвата исключения в проекте."""


class ErrorInURLNaming(YaCutErrors):
    """Ошибка при генерации короткой ссылки."""


class ErrorInDBSave(YaCutErrors):
    """Ошибка при создании объекта в базе данных."""


class AsyncGetUploadURLError(YaCutErrors):
    """Ошибка при получении ссылки для скачивания."""


class AsyncUploadFileError(YaCutErrors):
    """Ошибка при загрузке файла на ЯндексДиск."""


class AsyncGetDownloadURLError(YaCutErrors):
    """Ошибка при получении ссылки для скачивания."""


class InvalidAPIUsage(Exception):
    """Исключение для API."""

    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None):
        """Инициализация класса."""
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    @property
    def to_dict(self):
        """Возврат ошибки в словаре как атрибута."""
        return dict(message=self.message)


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    """Хендлер для ловли исключений InvalidAPIUsage."""
    return jsonify(error.to_dict), error.status_code
