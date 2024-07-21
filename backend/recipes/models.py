import shortuuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import (
    MAX_LENGTH_EMAIL_ADDRESS,
    MAX_LENGTH_FIRST_NAME,
    MAX_LENGTH_LAST_NAME,
    MAX_LENGTH_NAME,
    MAX_LENGTH_SLUG,
    MAX_LENGTH_TEXT,
    MAX_LENGTH_UNIT,
    MAX_LENGTH_USERNAME,
)

from .validators import (
    validate_max_amount,
    validate_max_cooking_time,
    validate_min_amount,
    validate_min_cooking_time,
)


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        max_length=MAX_LENGTH_USERNAME,
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL_ADDRESS,
        unique=True,
        verbose_name='email'
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_FIRST_NAME,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_LAST_NAME,
        verbose_name='Фамилия пользователя'
    )
    avatar = models.ImageField(
        upload_to='users/images/',
        null=True,
        default=None
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_staff or self.is_superuser


class Subscriptions(models.Model):
    """Модель подписки пользователя на других пользователей."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='subscribers',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчики',
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_user_author_subscription'
            ),
        )

    def __str__(self):
        return (f'{self.user.username[:MAX_LENGTH_NAME]} подписался '
                f'на {self.author.username[:MAX_LENGTH_NAME]}')


class Tag(models.Model):
    """Модель тега для рецептов."""

    name = models.CharField(
        verbose_name='Тэг',
        max_length=MAX_LENGTH_NAME,
        unique=True,
    )
    slug = models.CharField(
        verbose_name='Слаг тэга',
        max_length=MAX_LENGTH_SLUG,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name[:MAX_LENGTH_NAME]}'


class Ingredient(models.Model):
    """Модель ингредиента для рецептов."""

    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=MAX_LENGTH_NAME,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=MAX_LENGTH_UNIT,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredient_name_unit',
            ),
        )

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(
        verbose_name='Название блюда',
        max_length=MAX_LENGTH_NAME
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор рецепта',
        on_delete=models.SET_NULL,
        null=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты блюда',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
    )
    text = models.TextField(
        verbose_name='Описание блюда',
        max_length=MAX_LENGTH_TEXT
    )
    image = models.ImageField(
        verbose_name='Изображение блюда',
        upload_to='recipe_images/'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        validators=[validate_min_cooking_time, validate_max_cooking_time],
    )
    short_url = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True
    )

    class Meta:
        default_related_name = '%(class)ss'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author',),
                name='unique_recipe_title_author',
            ),
        )

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = shortuuid.ShortUUID().random(length=10)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name[:MAX_LENGTH_NAME]


class RecipeIngredient(models.Model):
    """Модель связи рецепта и ингредиента."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Связанные ингредиенты',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Связанные ингредиенты',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=[validate_min_amount, validate_max_amount],
    )

    class Meta:
        default_related_name = '%(class)ss'
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='unique_recipe_ingredient',
            ),
        )

    def __str__(self):
        return (f'{self.amount} {self.ingredient.measurement_unit} из '
                f'{self.ingredient.name} для {self.recipe.name}')


class TagRecipe(models.Model):
    """ Модель связи тега и рецепта."""

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class Favorite(models.Model):
    """Модель избранных рецептов пользователя."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Понравившиеся рецепты'
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        default_related_name = '%(class)ss'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user',),
                name='unique_user_favorite_recipe'
            ),
        )

    def __str__(self):
        return (f'{self.user.username} добавил(а) '
                f'в избранное {self.recipe.name}')


class ShoppingCart(models.Model):
    """Модель списка покупок пользователя."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Владелец списка',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты в списке покупок',
        on_delete=models.CASCADE
    )

    class Meta:
        default_related_name = '%(class)ss'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user',),
                name='unique_favorite_recipe'
            ),
        )

    def __str__(self):
        return (f'{self.user.username} включил '
                f'в список покупок {self.recipe.name}')
