import io
from datetime import datetime

from django.utils.translation import gettext as _


def get_correct_measurement(amount, measurement):
    measurement_plural = measurement + 's'
    return _(measurement_plural)


def generate_txt(ingredients, recipes):
    """Создает из списка ингредиентов текстовый файл."""
    buffer = io.StringIO()

    current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    buffer.write(f'Список покупок от {current_date}\n\n')

    buffer.write('Рецепты:\n')
    for idx, recipe in enumerate(recipes, start=1):
        buffer.write(f'{idx}. {recipe}\n')
    buffer.write('\n')

    buffer.write('Ингредиенты:\n')
    for idx, ingredient in enumerate(ingredients, start=1):
        name = ingredient.get('name').capitalize()
        measurement = ingredient.get('measurement')
        amount = ingredient.get('amount')
        correct_measurement = get_correct_measurement(amount, measurement)
        buffer.write(f'{idx}. {name}: {amount} {correct_measurement}\n')

    buffer.seek(0)
    return buffer
