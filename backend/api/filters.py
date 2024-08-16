import django_filters
from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    """Список фильтров для рецептов."""

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

    def filter_is_favorited(self, recipe, name, value):
        """Возвращает рецепты по фильтру "в избранном"."""
        if value:
            if self.request.user.is_authenticated:
                return recipe.filter(favorites__user=self.request.user)
            return recipe.none()
        return recipe

    def filter_is_in_shopping_cart(self, recipe, name, value):
        """Возвращает рецепты по фильтру "в корзине"."""
        value = bool(value)
        if value:
            if self.request.user.is_authenticated:
                return recipe.filter(shoppingcarts__user=self.request.user)
            return recipe.none()
        return recipe

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
