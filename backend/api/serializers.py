from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    User,
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)
from recipes.validators import ValidateUsername


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
        validators = [ValidateUsername()]

    def create(self, validated_data):
        """Создаёт нового пользователя c хешированием пароля."""
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
        validators = [ValidateUsername()]

    def get_is_subscribed(self, obj):
        """Проверяет подписку текущего пользователя на объект запроса."""
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.subscriptions.filter(
                following=obj
            ).exists()
        )


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

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок на авторов рецептов."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        """Возвращает True, так как сериализатор используется только для подписанных пользователей."""
        return True

    def get_recipes_count(self, obj):
        """Подсчитывает количество рецептов у автора."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Возвращает рецепты автора в соответствии с параметром 'recipes_limit' в запросе."""
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
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'unit')
        read_only_fields = ('id',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'ingredient', 'amount')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
            'pub_date',
            'cooking_time'
        )
        read_only_fields = ('id', 'author', 'pub_date')

    def get_is_favorited(self, recipe):
        """Проверяет есть ли рецепт в избранном."""
        user = self.context.get("request").user
        if user.is_authenticated:
            return recipe.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        """Проверяет есть ли рецепт в списке покупок."""
        user = self.context.get("request").user
        if user.is_authenticated:
            return recipe.shoppingcarts.filter(user=user).exists()
        return False

    def validate_image(self, value):
        """Проверяет, что поле изображение не пустое."""
        if not value:
            raise serializers.ValidationError(
                "Поле не может быть пустым, загрузите файл."
            )
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient_dict = ingredient_data['ingredient']
            ingredient, status = Ingredient.objects.get_or_create(
                **ingredient_dict
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )
        for tag_data in tags_data:
            tag, status = Tag.objects.get_or_create(**tag_data)
            recipe.tags.add(tag)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.title = validated_data.get('title', instance.title)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        instance.ingredients.clear()
        instance.tags.clear()
        for ingredient_data in ingredients_data:
            ingredient_dict = ingredient_data['ingredient']
            ingredient, status = Ingredient.objects.get_or_create(
                **ingredient_dict
            )
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )
        for tag_data in tags_data:
            tag, status = Tag.objects.get_or_create(**tag_data)
            instance.tags.add(tag)

        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    recipe = RecipeSerializer()

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe', 'date_added')
        read_only_fields = ('id', 'date_added', 'user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в списке избранного.'
            )
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        recipe_data = validated_data.pop('recipe')
        recipe, status = Recipe.objects.get_or_create(**recipe_data)
        favorite = Favorite.objects.create(user=request.user, recipe=recipe)
        return favorite


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    recipe = RecipeSerializer()

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')
        read_only_fields = ('id', 'user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в списке покупок.'
            )
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        recipe_data = validated_data.pop('recipe')
        recipe, status = Recipe.objects.get_or_create(**recipe_data)
        shopping_cart = ShoppingCart.objects.create(
            user=request.user, recipe=recipe
        )
        return shopping_cart
