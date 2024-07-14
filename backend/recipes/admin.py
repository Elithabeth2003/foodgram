from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from .models import Ingredient, Recipe, RecipeIngredient, Tag
from foodgram.constants import INGREDIENTS_PER_PAGE, OBJ_PER_PAGE


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('slug',)
    list_per_page = OBJ_PER_PAGE


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'unit',
    )
    search_fields = ('name',)
    list_per_page = INGREDIENTS_PER_PAGE


class RecipeIngredientInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        if not any(
            form.cleaned_data and not form.cleaned_data.get('DELETE', False)
            for form in self.forms
        ):
            raise ValidationError('Нужно добавить хотя бы 1 ингредиент.')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    formset = RecipeIngredientInlineFormSet


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'image',
        'text',
        'get_ingredients',
        'get_tags',
        'cooking_time',
        'favorites_count',
    )
    list_editable = ('name', 'text', 'image')
    search_fields = ('author__username', 'name')
    list_filter = ('tags__slug',)
    list_per_page = OBJ_PER_PAGE
    inlines = (RecipeIngredientInline,)

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        '''Возвращает название ингредиентов.'''
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    @admin.display(description='Теги')
    def get_tags(self, obj):
        '''Возвращает название тегов.'''
        return ', '.join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Добавлений в избранное')
    def favorites_count(self, obj):
        '''Возвращает кол-во добавлений рецепта в избранное.'''
        return obj.favorites.count()
