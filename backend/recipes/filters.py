from django.contrib import admin
from foodgram.constants import (
    SHORT, MEDIUM, LONG, MAX_TIME, MIN_TIME
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
            return queryset.filter(recipes__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(recipes__isnull=True)


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
            return queryset.filter(following__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(following__isnull=True)


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
            return queryset.filter(followers__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(followers__isnull=True)


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'время приготовления'
    parameter_name = 'cooking_time'

    thresholds = {
        SHORT: (None, MIN_TIME),
        MEDIUM: (MIN_TIME, MAX_TIME),
        LONG: (MAX_TIME, None)
    }

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        short_count = queryset.filter(cooking_time__lte=MIN_TIME).count()
        medium_count = queryset.filter(
            cooking_time__gt=MIN_TIME, cooking_time__lte=MAX_TIME
        ).count()
        long_count = queryset.filter(cooking_time__gt=MAX_TIME).count()
        return (
            (self.SHORT, f'быстрее 20 мин ({short_count})'),
            (self.MEDIUM, f'от 20 до 40 мин ({medium_count})'),
            (self.LONG, f'дольше 40 мин ({long_count})'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value in self.thresholds:
            min_time, max_time = self.thresholds[value]
            if min_time is not None and max_time is not None:
                return queryset.filter(
                    cooking_time__gte=min_time, cooking_time__lte=max_time
                )
            elif min_time is not None:
                return queryset.filter(cooking_time__gte=min_time)
            elif max_time is not None:
                return queryset.filter(cooking_time__lte=max_time)
        return queryset
