from foodgram.constants import (
    MAX_AMOUNT_INGREDIENTS,
    MIN_AMOUNT_INGREDIENTS,
    MIN_COOKING_TIME,
    MAX_COOKING_TIME
)
from django.core.exceptions import ValidationError


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
