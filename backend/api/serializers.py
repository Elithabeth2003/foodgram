import re

from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscriptions,
    Tag,
    User,
)
from foodgram.constants import MAX_AMOUNT_INGREDIENTS, MIN_AMOUNT_INGREDIENTS
from .validators import get_values_from_ingredients


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователей."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Создаёт нового пользователя c хешированием пароля."""
        username = validated_data.get('username')
        if not re.match(r'^[\w.@+-]+\Z', username):
            raise ValidationError(
                'Для поля "username" не должны приниматься значения, '
                'не соответствующие регулярному выражению "^[\w.@+-]+\Z"'
            )
        user = User(
            email=validated_data.get('email'),
            username=validated_data.get('username'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Проверяет подписку текущего пользователя на объект запроса."""
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Subscriptions.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate_avatar(self, value):
        """Проверяет, что поле аватар не пустое."""
        if not value:
            raise serializers.ValidationError(
                'Поле не может быть пустым, загрузите файл.'
            )
        return value


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe для списка подписок."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        """Возвращает URL изображения или пустую строку."""
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return ''


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок на авторов рецептов."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        """Переопределяет метод родительского класса."""
        return True

    def get_recipes_count(self, obj):
        """Подсчитывает кол-во рецептов у пользователя на которго подписан."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Возращает рецепты согласно параметру "recipes_limit" в запросе."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes = obj.recipes.all()[:recipes_limit]
            except ValueError:
                recipes = obj.recipes.all()
        else:
            recipes = obj.recipes.all()
        return ShortRecipeSerializer(
            recipes, many=True, context=self.context
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        read_only_fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    ingredients = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'ingredients',
            'tags',
            'text',
            'image',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )
        read_only_fields = ('id', 'author', 'pub_date')

    def validate_image(self, value):
        """Проверяет, что поле изображение не пустое."""
        if not value:
            raise serializers.ValidationError(
                'Поле не может быть пустым, загрузите файл.'
            )
        return value

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return ''

    def get_ingredients(self, recipe):
        """Возвращает ингредиенты рецепта."""
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeingredients__amount')
        )
        return ingredients

    def validate(self, data):
        """Проверяет поле тегов и ингредиентов."""
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        user = self.context.get('request').user
        if 'cooking_time' not in data:
            raise serializers.ValidationError(
                'Поле "cooking_time" не может быть пустым.'
            )
        if not ingredients:
            raise serializers.ValidationError(
                f'Поле {ingredients} не может быть пустым!'
            )
        ingredients_id_list = get_values_from_ingredients(ingredients, 'id')
        if len(ingredients_id_list) != len(set(ingredients_id_list)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными!'
            )
        ingredients_amount_list = get_values_from_ingredients(
            ingredients, 'amount'
        )
        if any(
            amount < MIN_AMOUNT_INGREDIENTS
            for amount in ingredients_amount_list
        ):
            raise serializers.ValidationError(
                f'Количество ингредиента '
                f'не может быть меньше {MIN_AMOUNT_INGREDIENTS}'
            )
        if any(
            amount > MAX_AMOUNT_INGREDIENTS
            for amount in ingredients_amount_list
        ):
            raise serializers.ValidationError(
                f'Количество ингредиентов '
                f'не может быть больше {MAX_AMOUNT_INGREDIENTS}'
            )

        existing_ingredients = Ingredient.objects.filter(
            id__in=ingredients_id_list
        ).values_list("id", flat=True)
        missing_ingredients = (
            set(ingredients_id_list) - set(existing_ingredients)
        )
        if missing_ingredients:
            raise serializers.ValidationError(
                f'Ингредиент(ы) с id {missing_ingredients} не существуют!'
            )
        if not tags:
            raise serializers.ValidationError(
                'Поле теги не может быть пустым!'
            )
        try:
            tags_id_list = [int(tag) for tag in tags]
        except ValueError:
            raise serializers.ValidationError(
                'Все значения id тегов должны быть целыми числами!'
            )
        if len(tags_id_list) != len(set(tags_id_list)):
            raise serializers.ValidationError('Теги должны быть уникальными!')

        existing_tags = Tag.objects.filter(
            id__in=tags_id_list
        ).values_list("id", flat=True)
        missing_tags = set(tags_id_list) - set(existing_tags)
        if missing_tags:
            raise serializers.ValidationError(
                f'Тег(ов) с id {missing_tags} не существует!'
            )
        data.update(
            {
                'tags': tags_id_list,
                'ingredients': ingredients,
                'author': user,
            }
        )
        return data

    def set_ingredients(self, recipe, ingredients):
        """Добавляет ингредиенты в промежуточную модель."""
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount'),
                    recipe=recipe,
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        """Создаёт новый рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        instance.ingredients.clear()
        self.set_ingredients(instance, ingredients_data)
        instance.tags.set(tags_data)
        return instance

    def get_is_favorited(self, recipe):
        """Проверяет, добавлен ли рецепт в избранное пользователем."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return recipe.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        """Проверяет, добавлен ли рецепт в список покупок пользователем."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return recipe.shoppingcarts.filter(user=user).exists()
        return False


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorite."""

    recipe = ShortRecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('recipe',)
        read_only_fields = ('recipe',)

    def validate(self, data):
        """Проверяет, что рецепт не добавлен в избранное ранее."""
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в списке избранного.'
            )
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingCart."""

    recipe = ShortRecipeSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('recipe',)
        read_only_fields = ('recipe',)

    def validate(self, data):
        """Проверяет, что рецепт не добавлен в список покупок ранее."""
        user = data['user']
        user = data['user']
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в списке покупок.'
            )
        return data
