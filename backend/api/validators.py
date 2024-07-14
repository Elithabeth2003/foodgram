from rest_framework import serializers

from recipes.models import Tag, Ingredient
from foodgram.constants import MAX_AMOUNT_INGREDIENTS, MIN_AMOUNT_INGREDIENTS


def get_values_from_ingredients(ingredients, key):
    """Проверяет список словарей ингредиентов."""
    try:
        ingredients_values_list = [
            int(ingredient.get(key)) for ingredient in ingredients
        ]
    except TypeError:
        raise serializers.ValidationError(
            "Поле ингредиенты должен быть списком словарей! "
            "В словаре должны быть значения ingredient id и "
            " amount! Например [{'id': 1123, 'amount': 10}]."
        )
    except ValueError:
        raise serializers.ValidationError(
            f"Все значения {key} ингредиентов должны быть целыми числами!"
        )
    return ingredients_values_list


def get_validated_tags(tags):
    """Валидирует теги."""
    if not tags:
        raise serializers.ValidationError(
            "Поле теги не может быть пустым! "
            "Добавьте хотя бы один тег в поле 'tags: [ tag_ids ]'."
        )
    try:
        tags_id_list = [int(tag) for tag in tags]
    except ValueError:
        raise serializers.ValidationError(
            "Все значения id тегов должны быть целыми числами!"
        )
    if len(tags_id_list) != len(set(tags_id_list)):
        raise serializers.ValidationError("Теги должны быть уникальными!")

    existing_tags = Tag.objects.filter(
        id__in=tags_id_list
    ).values_list("id", flat=True)
    missing_tags = set(tags_id_list) - set(existing_tags)
    if missing_tags:
        raise serializers.ValidationError(
            f"Тег(ов) с id {missing_tags} не существует!"
        )
    return tags


def get_validated_ingredients(ingredients):
    """Валидирует ингредиенты."""
    if not ingredients:
        raise serializers.ValidationError(
            "Поле ингредиенты не может быть пустым! "
            "Добавьте хотя бы один ингредиент в поле "
            "'ingredients'. Например [{'id': 1123, 'amount': 10}]."
        )

    ingredients_id_list = get_values_from_ingredients(ingredients, "id")
    if len(ingredients_id_list) != len(set(ingredients_id_list)):
        raise serializers.ValidationError(
            "Ингредиенты должны быть уникальными!"
        )

    ingredients_amount_list = get_values_from_ingredients(
        ingredients, key="amount"
    )
    if any(
        amount < MIN_AMOUNT_INGREDIENTS for amount in ingredients_amount_list
    ):
        raise serializers.ValidationError(
            "Количество ингредиента не может быть меньше "
            f"{MIN_AMOUNT_INGREDIENTS}"
        )
    if any(
        amount > MAX_AMOUNT_INGREDIENTS for amount in ingredients_amount_list
    ):
        raise serializers.ValidationError(
            "Количество ингредиентов не может быть больше "
            f"{MAX_AMOUNT_INGREDIENTS}"
        )

    existing_ingredients = Ingredient.objects.filter(
        id__in=ingredients_id_list
    ).values_list("id", flat=True)
    missing_ingredients = set(ingredients_id_list) - set(existing_ingredients)
    if missing_ingredients:
        raise serializers.ValidationError(
            f"Ингредиент(ы) с id {missing_ingredients} не существуют!"
        )
    return ingredients


def get_validated_id(id, url_path):
    """Проверяет id в url на соответствие целому числу."""
    try:
        validated_id = int(id)
    except ValueError:
        raise serializers.ValidationError(
            f"id в url {url_path}/id/ должен быть целым числом!"
        )
    return validated_id
