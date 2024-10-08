from datetime import datetime


def generate_txt(ingredients, recipes):
    """Создает из списка продуктов текстовый файл."""

    current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    return '\n'.join(
        [
            f'Список покупок от {current_date}\n',
            'Рецепты:',
            *[f'{index}. {recipe}' for index, recipe in enumerate(
                recipes, start=1
            )],
            '\nПродукты:',
            *[
                f'{index}. {ingredient["name"].capitalize()}: '
                f'{ingredient["amount"]} {ingredient["measurement"]}'
                for index, ingredient in enumerate(ingredients, start=1)
            ]
        ]
    )
