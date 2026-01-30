"""View-функции для API проекта YaCut."""

from flask import jsonify, request
from http import HTTPStatus

from . import app
from .constants import OPTIONAL_KEY, TO_DICT_SHORT_URL, REQUIRED_KEY
from .error_handlers import ErrorInDBSave, ErrorInURLNaming, InvalidAPIUsage
from .models import URLMap
from .utils import get_unique_short_id, validate_api_data


@app.route('/api/id/', methods=['POST'])
def get_short_url():
    """Получение короткой ссылки через API."""
    data = request.get_json(silent=True)
    validate_api_data(data)
    short_url = data.get(OPTIONAL_KEY, '')

    try:
        short_id = get_unique_short_id(
            data[REQUIRED_KEY], short_url
        )
    except ErrorInURLNaming:
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.'
        )
    except ErrorInDBSave:
        raise InvalidAPIUsage('Ошибка сохранения записи в БД.')

    result = {
        'url': data[REQUIRED_KEY],
        TO_DICT_SHORT_URL: request.host_url + short_id
    }
    return jsonify(result), HTTPStatus.CREATED


@app.route('/api/id/<short_id>/', methods=['GET'])
def redirect_api(short_id: str):
    """Метод возвращает полную ссылку по короткой."""
    link = URLMap.query.filter_by(short=short_id).first()

    if link is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)

    return jsonify({'url': link.original})
