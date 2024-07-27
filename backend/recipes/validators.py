from django.core.exceptions import ValidationError
import re
from django.conf import settings


def validate_username(username):
    if username == settings.USER_PROFILE_URL:
        raise ValidationError(
            f'Имя пользователя {settings.USER_PROFILE_URL} не разрешено.'
        )
    if not re.match(r'^[\w.@+-]+\Z', username):
        invalid_str = ''.join(set(re.findall(r'[^\w.@+-]', username)))
        raise ValidationError(
            f'Недопустимые символы в имени пользователя: {invalid_str}'
        )
