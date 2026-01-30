"""Формы для проекта YaCut."""

from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import SubmitField, URLField
from wtforms.validators import DataRequired, Length, URL

from .constants import LINK
from .validators import ValidateShortURL


class URLForm(FlaskForm):
    """Форма для создания коротких ссылок."""

    original_link = URLField(
        'Длинная ссылка',
        validators=[
            Length(
                max=LINK,
                message='Слишком длинная ссылка.'
            ),
            DataRequired(message='Обязательное поле'),
            URL(message='Некорректный адрес', require_tld=True),
        ]
    )
    custom_id = URLField(
        'Ваш вариант короткой ссылки',
        validators=[ValidateShortURL()]
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
