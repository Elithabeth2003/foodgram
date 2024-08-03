from django.contrib import admin
from django.db.models import Count

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
        if self.value() == 'yes':
            return queryset.annotate(
                recipe_count=Count('recipes')
            ).filter(recipe_count__gt=0)
        if self.value() == 'no':
            return queryset.annotate(
                recipe_count=Count('recipes')
            ).filter(recipe_count__exact=0)


class HasSubscriptionsFilter(admin.SimpleListFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.annotate(
                subscription_count=Count('following')
            ).filter(subscription_count__gt=0)
        if self.value() == 'no':
            return queryset.annotate(
                subscription_count=Count('following')
            ).filter(subscription_count__exact=0)


class HasFollowersFilter(admin.SimpleListFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_followers'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.annotate(
                follower_count=Count('followers')
            ).filter(follower_count__gt=0)
        if self.value() == 'no':
            return queryset.annotate(
                follower_count=Count('followers')
            ).filter(follower_count__exact=0)


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time'

    COOKING_TIME_RANGES = [
        (
            RANGE_1_START, RANGE_1_END,
            f'от {RANGE_1_START} минуты до {RANGE_1_END} минут'
        ),
        (
            RANGE_2_START, RANGE_2_END,
            f'от {RANGE_2_START} минуты до {RANGE_2_END} минут'
        ),
        (
            RANGE_3_START, RANGE_3_END,
            f'от {RANGE_3_START} минуты до {RANGE_3_END} минут'
        ),
    ]

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        return [
            (f'{start}-{end}',
             f'''{label} ({
                queryset.filter(
                    cooking_time__gte=start, cooking_time__lte=end
                ).count()
            })''')
            for start, end, label in self.COOKING_TIME_RANGES
        ]

    def queryset(self, request, queryset):
        if self.value():
            start, end = map(int, self.value().split('-'))
            return queryset.filter(
                cooking_time__gte=start, cooking_time__lte=end
            )
        return queryset
