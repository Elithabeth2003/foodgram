import re

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_username(username):
    """Проверка имени пользователя на соответствие шаблону."""
    if username == settings.USER_PROFILE_URL:
        raise ValidationError(
            (f'Использовать имя {settings.USER_PROFILE_URL} '
             'в качестве username запрещено!')
        )
    matching_chars = re.findall(r'[^\w.@+-]+', username)
    if matching_chars:
        raise ValidationError(
            f'Поле \'username\' содержит '
            f'недопустимые символы: {set(matching_chars)}'
        )
