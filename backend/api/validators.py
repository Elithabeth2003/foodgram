from rest_framework import serializers


def get_values_from_ingredients(ingredients, key):
    """Проверяет список словарей ингредиентов."""
    try:
        ingredients_values_list = [
            int(ingredient.get(key)) for ingredient in ingredients
        ]
    except TypeError:
        raise serializers.ValidationError(
            'Поле ингредиенты должен быть списком словарей!'
        )
    except ValueError:
        raise serializers.ValidationError(
            f'Все значения {key} ингредиентов должны быть целыми числами!'
        )
    return ingredients_values_list
