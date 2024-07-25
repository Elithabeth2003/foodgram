from django.contrib import admin


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

    def lookups(self, request, model_admin):
        return (
            ('short', 'быстрее 20 мин'),
            ('medium', 'от 20 до 40 мин'),
            ('long', 'дольше 40 мин'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'short':
            return queryset.filter(cooking_time__lt=20)
        if self.value() == 'medium':
            return queryset.filter(cooking_time__gte=20, cooking_time__lte=40)
        if self.value() == 'long':
            return queryset.filter(cooking_time__gt=40)
        return queryset
