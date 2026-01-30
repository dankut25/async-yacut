"""Формы для проекта YaCut."""

from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp, URL

from .constants import CORRECT_SYMBOLS, LINK, SHORT_LINK_MAX


class URLForm(FlaskForm):
    """Форма для создания коротких ссылок."""

    original_link = URLField(
        'Длинная ссылка',
        validators=[
            Length(
                1,
                LINK,
                message='Слишком длинная ссылка.'
            ),
            DataRequired(message='Обязательное поле'),
            URL(message='Некорректный адрес', require_tld=True),
        ]
    )
    custom_id = URLField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(
                1,
                SHORT_LINK_MAX,
                message=(
                    f'Длина должна быть от 1 до {SHORT_LINK_MAX} символов.'
                )
            ),
            Regexp(
                CORRECT_SYMBOLS,
                message='Можно использовать только латинские буквы и цифры'
            ),
            Optional()
        ]
    )
    submit = SubmitField('Создать')


class FileUploadForm(FlaskForm):
    """Форма для загрузки файлов."""

    files = MultipleFileField(
        'Файл не выбран',
        validators=[
            DataRequired(message='Выберите файлы'),
        ]
    )
    submit = SubmitField('Загрузить')
