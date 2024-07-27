from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    User,
    Subscriptions,
    Tag, Ingredient,
    Recipe,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
)

from .filters import (
    HasRecipesFilter,
    HasSubscriptionsFilter,
    HasFollowersFilter,
    CookingTimeFilter
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'recipe_count',
        'subscription_count',
        'follower_count'
    )
    search_fields = ('email', 'username')
    list_filter = (
        HasRecipesFilter,
        HasSubscriptionsFilter,
        HasFollowersFilter,
    )

    @admin.display(description='Рецепты')
    def recipe_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписки')
    def subscription_count(self, user):
        return user.authors.count()

    @admin.display(description='Подписчики')
    def follower_count(self, user):
        return user.followers.count()


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipe_count')
    search_fields = ('name',)

    @admin.display(description='Число рецептов')
    def recipe_count(self, tag):
        return tag.recipes.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipe_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description='Число рецептов')
    def recipe_count(self, ingredient):
        return ingredient.recipeingredients.count()


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'cooking_time',
        'display_tags',
        'display_ingredients',
        'display_image',
        'favorite_count'
    )
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('tags', CookingTimeFilter)
    readonly_fields = ('favorite_count',)

    inlines = [RecipeIngredientInline]

    @admin.display(description='Теги')
    @mark_safe
    def display_tags(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Продукты')
    @mark_safe
    def display_ingredients(self, recipe):
        return '<br>'.join(
            f'{ingr.name} ({ingr.measurement_unit}) - {recipe_ingr.amount}'
            for ingr in recipe.ingredients.all()
            for recipe_ingr in RecipeIngredient.objects.filter(
                recipe=recipe, ingredient=ingr
            )
        )

    @admin.display(description='Изображение')
    def display_image(self, recipe):
        return format_html(
            '<img src="{}" style="max-height: 100px;">', recipe.image.url
        )

    @admin.display(description='Избранное')
    def favorite_count(self, recipe):
        return recipe.favorite_set.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
