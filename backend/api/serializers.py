from rest_framework import serializers
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
from recipes.constants import MIN_INGREDIENT_AMOUNT


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для создания и представления пользователей."""

    is_subscribed = serializers.SerializerMethodField()
    email = serializers.EmailField(required=True, allow_blank=False)
    # без явного определения он не видит емейл

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            *DjoserUserSerializer.Meta.fields,
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and Subscriptions.objects.filter(
                user=request.user, author=user
            ).exists()
        )

    def create(self, validated_data):  # он самостоятельно не хеширует пароль
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe для списка подписок."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор для подписок на авторов рецептов."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, recipe):
        """Возращает рецепты согласно параметру "recipes_limit" в запросе."""
        return ShortRecipeSerializer(
            recipe.recipes.all()[:int(
                self.context.get('request').GET.get('recipes_limit', 10**10)
            )], many=True, context=self.context
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
        source='ingredient', read_only=True
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='name'
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        """Проверяет, что количество ингредиента не меньше минимального."""
        if value < MIN_INGREDIENT_AMOUNT:
            raise serializers.ValidationError(
                f'Количество продукта ({value}) '
                f'меньше минимально допустимого ({MIN_INGREDIENT_AMOUNT}).'
            )
        return value


class RecipeRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта с использованием slug."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredients', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'ingredients',
            'tags',
            'text',
            'image',
            'cooking_time',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )
        read_only_fields = fields

    def get_is_favorited(self, recipe):
        """Проверяет, добавлен ли рецепт в избранное пользователем."""
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and recipe.favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        """Проверяет, добавлен ли рецепт в список покупок пользователем."""
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and recipe.shoppingcarts.filter(user=user).exists()
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта с использованием id."""

    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'name',
            'ingredients',
            'tags',
            'text',
            'image',
            'cooking_time',
            'id',
        )
        read_only_fields = ('author',)

    def to_representation(self, instance):
        """Возвращает данные сериализатора для GET-запроса."""
        return RecipeRetrieveSerializer(instance, context=self.context).data

    def validate_image(self, value):
        """Проверяет, что поле изображение не пустое."""
        if not value:
            raise serializers.ValidationError(
                'Поле не может быть пустым, загрузите файл.'
            )
        return value

    @staticmethod
    def validate_items(items, model, field_name):
        existing_items = model.objects.filter(
            id__in=items
        ).values_list('id', flat=True)
        missing_items = set(items) - set(existing_items)
        if missing_items:
            raise serializers.ValidationError(
                {field_name: f'Элемент(ы) с id {missing_items} не существует!'}
            )
        non_unique_ids = set(
            item for item in items if items.count(item) > 1
        )
        if non_unique_ids:
            raise serializers.ValidationError(
                {field_name: f'Элементы с id {non_unique_ids} не уникальны!'}
            )

    def validate(self, data):
        """Проверяет поля теги и ингредиенты."""
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        ingredients_ids = [item['id'] for item in ingredients]
        self.validate_items(
            ingredients_ids,
            model=Ingredient,
            field_name='ingredients',
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
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=recipe,
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        """Создаёт новый рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.save()
        instance.ingredients.clear()
        self.set_ingredients(instance, ingredients_data)
        instance.tags.set(tags_data)
        return super().update(instance, validated_data)
