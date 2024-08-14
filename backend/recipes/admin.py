from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html

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

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'recipe_count',
        'subscription_count',
        'follower_count',
        'avatar'
    )
    search_fields = ('email', 'username')
    list_filter = (
        HasRecipesFilter,
        HasSubscriptionsFilter,
        HasFollowersFilter,
    )

    @admin.display(description='Рецепты')
    def recipe_count(self, user):
        count = user.recipes.count()
        if count:
            url = reverse(
                'admin:recipes_recipe_changelist'
            ) + f'?author__id={user.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count

    @admin.display(description='Подписки')
    def subscription_count(self, user):
        count = user.authors.count()
        if count:
            url = reverse('admin:recipes_subscriptions_changelist')
            return format_html('<a href="{}">{}</a>', url, count)
        return count

    @admin.display(description='Подписчики')
    def follower_count(self, user):
        count = user.followers.count()
        if count:
            url = reverse('admin:recipes_subscriptions_changelist')
            return format_html('<a href="{}">{}</a>', url, count)
        return count

    @admin.display(description='Аватар')
    @mark_safe
    def avatar_image(self, user):
        return (
            f'<img src="{user.avatar.url}" width="50" height="50" />'
        )


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
    exclude = ('slug_for_short_url',)

    inlines = [RecipeIngredientInline]

    @admin.display(description='Теги')
    @mark_safe
    def display_tags(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Продукты')
    @mark_safe
    def display_ingredients(self, recipe):
        return '<br>'.join(
            f'{ri.ingredient.name} '
            f'({ri.ingredient.measurement_unit}) - {ri.amount}'
            for ri in recipe.recipeingredients.all()
        )

    @admin.display(description='Изображение')
    @mark_safe
    def display_image(self, recipe):
        return '<img src="{}" style="max-height: 100px;">'.format(
            recipe.image.url
        )

    @admin.display(description='Избранное')
    def favorite_count(self, recipe):
        return recipe.favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
