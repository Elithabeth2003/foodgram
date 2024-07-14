from django_filters import (
    CharFilter,
    NumberFilter,
    FilterSet,
)
from django.db.models import Q

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """Список фильтров для рецептов."""

    author = NumberFilter(field_name="author__id")
    tags = CharFilter(method="filter_tags")
    is_favorited = NumberFilter(method="filter_is_favorited")
    is_in_shopping_cart = NumberFilter(method="filter_is_in_shopping_cart")

    def filter_tags(self, queryset, name, value):
        """Возвращает рецепты по фильтру "теги" если они существуют."""
        if not value:
            return queryset

        tags = value.split(",")
        existing_tags = Tag.objects.filter(slug__in=tags)
        if not existing_tags.exists():
            return queryset.none()

        q_objects = Q()
        for tag in existing_tags:
            q_objects |= Q(tags__slug=tag.slug)
        return queryset.filter(q_objects).distinct()

    def filter_is_favorited(self, queryset, name, value):
        """Возвращает рецепты по фильтру "в избранном"."""
        value = bool(value)
        if value:
            if self.request.user.is_authenticated:
                return queryset.filter(favorites__user=self.request.user)
            return queryset.none()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Возвращает рецепты по фильтру "в корзине"."""
        value = bool(value)
        if value:
            if self.request.user.is_authenticated:
                return queryset.filter(in_carts__user=self.request.user)
            return queryset.none()
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")


class IngredientFilter(FilterSet):
    """Фильтр по названию для ингредиентов."""

    name = CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Ingredient
        fields = ("name",)