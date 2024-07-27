from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from foodgram.constants import (
    MAX_LENGTH_EMAIL_ADDRESS,
    MAX_LENGTH_FIRST_NAME,
    MAX_LENGTH_LAST_NAME,
    MAX_LENGTH_NAME,
    MAX_LENGTH_SLUG,
    MAX_LENGTH_TEXT,
    MAX_LENGTH_UNIT,
    MAX_LENGTH_USERNAME,
    MIN_COOKING_TIME,
    MIN_AMOUNT_INGREDIENTS,
)

from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        max_length=MAX_LENGTH_USERNAME,
        validators=[validate_username],
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL_ADDRESS,
        unique=True,
        verbose_name='Электронная почта'
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_FIRST_NAME,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_LAST_NAME,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='users/images/',
        null=True,
        default=None
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    """Модель подписки пользователя на других пользователей."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='authors',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчики',
        related_name='followers',
        on_delete=models.CASCADE,
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
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME,
        unique=True,
    )
    slug = models.CharField(
        verbose_name='Идентификатор',
        max_length=MAX_LENGTH_SLUG,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_LENGTH_NAME]


class Ingredient(models.Model):
    """Модель ингредиента для рецептов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=MAX_LENGTH_UNIT,
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
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
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор',
        on_delete=models.SET_NULL,
        null=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Продукты',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
    )
    text = models.TextField(
        verbose_name='Описание',
        max_length=MAX_LENGTH_TEXT
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe_images/'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(MIN_COOKING_TIME)
        ]
    )
    slug_for_short_url = models.CharField(
        verbose_name='Слаг для короткой ссылки',
        max_length=10,
        unique=True,
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
        if not self.slug_for_short_url:
            self.slug_for_short_url = str(self.id)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name[:MAX_LENGTH_NAME]


class RecipeIngredient(models.Model):
    """Модель связи рецепта и ингредиента."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Связанные рецепты',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Связанные продукты',
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_AMOUNT_INGREDIENTS)
        ]
    )

    class Meta:
        default_related_name = '%(class)ss'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
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


class UserRecipeBase(models.Model):
    """Базовая модель для связи пользователя и рецепта."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)ss'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='%(class)s_unique_user_recipe'
            ),
        )

    def __str__(self):
        return f'{self.user.username} взаимодействует с {self.recipe.name}'


class Favorite(UserRecipeBase):
    """Модель избранных рецептов пользователя."""

    class Meta(UserRecipeBase.Meta):
        verbose_name = _('Избранный рецепт')
        verbose_name_plural = _('Избранные рецепты')

    def __str__(self):
        return f'{self.user.username} добавил в избранное {self.recipe.name}'


class ShoppingCart(UserRecipeBase):
    """Модель списка покупок пользователя."""

    class Meta(UserRecipeBase.Meta):
        verbose_name = _('Список покупок')
        verbose_name_plural = _('Списки покупок')

    def __str__(self):
        return (
            f'{self.user.username} добавил '
            f'в список покупок {self.recipe.name}'
        )
