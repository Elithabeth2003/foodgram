import re
from foodgram.constants import (
    MAX_AMOUNT_INGREDIENTS,
    MIN_AMOUNT_INGREDIENTS,
    MIN_COOKING_TIME,
    MAX_COOKING_TIME
)
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.deconstruct import deconstructible


@deconstructible
class ValidateUsername:
    def validate_username(self, username):
        """Проверка имени пользователя на соответствие шаблону."""
        if username == settings.USER_PROFILE_URL:
            raise ValidationError(
                (f'Использовать имя {settings.USER_PROFILE_URL} '
                 'в качестве username запрещено!')
            )
        matching_chars = re.findall(r'[^\w.@+-]+', username)
        if matching_chars:
            ''.join(set(matching_chars))
            raise ValidationError(
                f'Поле \'username\' содержит '
                f'недопустимые символы: {set(matching_chars)}'
            )
        return username

    def __call__(self, value):
        return self.validate_username(value)


def validate_min_cooking_time(value):
    if value < MIN_COOKING_TIME:
        raise ValidationError('Ваше блюдо уже готово!')


def validate_max_cooking_time(value):
    if value > MAX_COOKING_TIME:
        raise ValidationError('Слишком долго ждать')


def validate_min_amount(value):
    if value < MIN_AMOUNT_INGREDIENTS:
        raise ValidationError(
            f'Количество не может быть меньше {MIN_AMOUNT_INGREDIENTS}.'
        )


def validate_max_amount(value):
    if value > MAX_AMOUNT_INGREDIENTS:
        raise ValidationError(
            f'Количество не может быть больше {MAX_AMOUNT_INGREDIENTS}.'
        )
