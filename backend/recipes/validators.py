from django.core.exceptions import ValidationError
import re
from django.conf import settings


def validate_username(value):
    if value.lower() == settings.USER_PROFILE_URL:
        raise ValidationError(f'Имя пользователя {settings} не разрешено.')
    matching_chars = re.compile(r'^[\w.@+-]+\Z')
    if not matching_chars.match(value):
        raise ValidationError(
            'Имя пользователя может содержать '
            'только буквы, цифры и знаки @/./+/-/_.'
        )
