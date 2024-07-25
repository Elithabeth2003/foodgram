from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserSerializer as DjoserUserSerializer

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Subscriptions,
    Tag,
    User,
)
from foodgram.constants import MIN_AMOUNT_INGREDIENTS
from recipes.validators import validate_username


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для создания и представления пользователей."""

    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(
        write_only=True, style={'input_type': 'password'}, required=False
    )

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + (
            'password',
            'is_subscribed',
            'avatar'
        )

    def create(self, validated_data):
        """Создает нового пользователя с хешированием пароля."""
        username = validated_data.get('username')
        email = validated_data.get('email')
        validate_username(username)
        if not email:
            raise ValidationError('Поле "email" не может быть пустым.')

        user = User(
            email=validated_data.get('email'),
            username=username,
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    def get_is_subscribed(self, user):
        """Проверяет подписку текущего пользователя на объект запроса."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscriptions.objects.filter(
                user=request.user, author=user
            ).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate_avatar(self, avatar):
        """Проверяет, что поле аватар не пустое."""
        if not avatar:
            raise serializers.ValidationError(
                'Поле не может быть пустым, загрузите файл.'
            )
        return avatar


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe для списка подписок."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок на авторов рецептов."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )
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

    def get_is_subscribed(self, subscribe):
        """Переопределяет метод родительского класса."""
        return True

    def get_recipes(self, obj):
        """Возращает рецепты согласно параметру "recipes_limit" в запросе."""
        request = self.context.get('request')
        recipes_limit = int(request.GET.get('recipes_limit', 10**10))
        recipes = obj.recipes.all()[:recipes_limit]
        return ShortRecipeSerializer(
            recipes, many=True, context=self.context
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', read_only=True
    )
    name = serializers.CharField(
        source='ingredient.name', read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    ingredients = RecipeIngredientSerializer(many=True)
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

    def validate(self, data):
        """Проверяет поля теги и ингредиенты."""
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        self.validate_items(
            ingredients,
            model=Ingredient,
            field_name='ingredients',
            min_amount=MIN_AMOUNT_INGREDIENTS,
        )
        self.validate_items(
            tags,
            model=Tag,
            field_name='tags',
        )
        return data

    def set_ingredients(self, recipe, ingredients):
        """Добавляет ингредиенты в промежуточную модель."""
        RecipeIngredient.objects.bulk_create(
                RecipeIngredient(
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount'),
                    recipe=recipe,
                )
                for ingredient in ingredients
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
        super().update(instance, validated_data)
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
