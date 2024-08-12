from django.contrib import admin
from ast import literal_eval

from .constants import (
    RANGE_1_START,
    RANGE_1_END,
    RANGE_2_START,
    RANGE_2_END,
    RANGE_3_START,
    RANGE_3_END
)


class HasRecipesFilter(admin.SimpleListFilter):
    title = 'Есть рецепты'
    parameter_name = 'has_recipes'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() in ['yes', 'no']:
            has_recipes = self.value() == 'yes'
            return queryset.filter(recipes__isnull=not has_recipes)


class HasSubscriptionsFilter(admin.SimpleListFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() in ['yes', 'no']:
            has_subscriptions = self.value() == 'yes'
            return queryset.filter(following__isnull=not has_subscriptions)


class HasFollowersFilter(admin.SimpleListFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_followers'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() in ['yes', 'no']:
            has_followers = self.value() == 'yes'
            return queryset.filter(followers__isnull=not has_followers)


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time'

    COOKING_TIME_RANGES = [
        (
            RANGE_1_START, RANGE_1_END,
            f'До {RANGE_1_END} минут'
        ),
        (
            RANGE_2_START, RANGE_2_END,
            f'От {RANGE_1_END} минуты до {RANGE_2_END} минут'
        ),
        (
            RANGE_3_START, RANGE_3_END,
            f'От {RANGE_2_END}'
        ),
    ]

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        return [
            (start, end,
             f'{label} '
             f'({self.get_filtered_queryset(queryset, start, end).count()})')
            for start, end, label in self.COOKING_TIME_RANGES
        ]

    def queryset(self, request, queryset):
        if self.value():
            start, end = literal_eval(self.value())
            return self.get_filtered_queryset(queryset, start, end)
        return queryset

    def get_filtered_queryset(self, queryset, start, end):
        return queryset.filter(cooking_time__range=(start, end))
