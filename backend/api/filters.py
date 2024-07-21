import django_filters
from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    """Список фильтров для рецептов."""

    author = django_filters.NumberFilter(field_name='author__id')
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        conjoined=False
    )

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
                return queryset.filter(shoppingcarts__user=self.request.user)
            return queryset.none()
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart', 'tags')


class IngredientFilter(django_filters.FilterSet):
    """Фильтр по названию для ингредиентов."""

    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
