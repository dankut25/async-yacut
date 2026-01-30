"""Валидаторы для проекта YaCut."""

import re

from typing import Any, Optional
from wtforms import Form, Field
from wtforms.validators import ValidationError

from .constants import CORRECT_SYMBOLS, SHORT_LINK_MAX


class ShortURLValidator:
    """Универсальный валидатор для коротких ссылок.

    Можно инициализировать только не пустой строкой.
    При создании объекта класса методом create, вернет
    None если переданный параметр не является строкой, иначе
    вернет объект класса.
    В класс есть два валидатора длины строки и сравнение символов
    с образцом через re.
    """

    def __init__(self, text: Any):
        """Инициализация валидатора."""
        if not text or not isinstance(text, str):
            raise ValueError(
                'Инициализировать можно только не пустой строкой.'
            )

        self.text = text

    @classmethod
    def create(cls, text: Any):
        """Создаем класс проверки из строки или возращаем None."""
        if not text or not isinstance(text, str):
            return None

        return cls(text)

    def check_length(self, limit: int) -> bool:
        """Проверка длины строки."""
        if not isinstance(limit, int) or limit < 1:
            raise ValueError(
                '\"limit\" - должен быть целым положительным числом > 0'
            )
        return len(self.text) <= limit

    def pattern_validation(self, pattern: str) -> bool:
        """Валидация строки на корректные символы по образцу."""
        return re.match(pattern, self.text) is not None

    def check_all(self, limit: int, pattern: str) -> bool:
        """Проверка двух условий сразу.

        Проверка на допустимую длину и корректность символов.
        """
        return all(
            [self.check_length(limit), self.pattern_validation(pattern)]
        )


class ValidateShortURL():
    """Валидатор для символов произвольной короткой ссылки.

    Разрешены только латинские заглавные и строчные буквы,
    цифры от 0 до 9.
    """

    def __init__(self, message: Optional[str] = None):
        """Инициализация класса валидатора."""
        self.message = message

    def __call__(self, _: Form, field: Field):
        """Проверка условия и возврат ошибки."""
        validator = ShortURLValidator.create(field.data)

        if validator is not None:
            if not validator.check_length(SHORT_LINK_MAX):
                raise ValidationError(
                    f'Длина должна быть от 1 до {SHORT_LINK_MAX} символов.'
                )

            if not validator.pattern_validation(CORRECT_SYMBOLS):
                raise ValidationError(
                    'Можно использовать только латинские буквы и цифры'
                )
