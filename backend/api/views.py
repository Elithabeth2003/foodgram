from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscriptions,
    Tag,
    User,
)
from foodgram.constants import PDF_FILENAME, SHORT_LINK_URL_PATH
from .filters import IngredientFilter, RecipeFilter
from .mixins import DjoserPermissionsMethodsMixin
from .paginators import PaginatorWithLimit
from .permissions import ReadOnlyOrIsAuthenticatedOrAuthor
from .serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    UserSerializer,
)
from .utils import generate_pdf


class UserViewSet(DjoserUserViewSet, DjoserPermissionsMethodsMixin):
    """ViewSet для управления пользователями."""
    pagination_class = PaginatorWithLimit

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        """Возвращает данные текущего пользователя."""
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Обновляет или удаляет аватар текущего пользователя."""
        if request.method == 'PUT':
            serializer = AvatarSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            request.user.avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        """
        Возвращает список пользователей, на которых подписан пользователь.
        """
        subscriptions = User.objects.filter(subscriptions__user=request.user)
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionsSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionsSerializer(
            subscriptions, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        """Подписка и отписка текущего пользователя от другого пользователя."""
        user_to_follow = get_object_or_404(User, pk=id)
        user = request.user

        if user == user_to_follow:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == 'POST':
            _, created = Subscriptions.objects.get_or_create(
                user=user, author=user_to_follow
            )
            if created:
                serializer = SubscriptionsSerializer(
                    user_to_follow, context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        elif request.method == 'DELETE':
            subscription = Subscriptions.objects.filter(
                user=user, author=user_to_follow
            ).first()
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Вы не были подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для управления тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для управления ингридиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [permissions.AllowAny]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для управления рецептами."""

    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    pagination_class = PaginatorWithLimit
    permission_classes = [ReadOnlyOrIsAuthenticatedOrAuthor]
    filterset_class = RecipeFilter

    @action(
        detail=True,
        permission_classes=[permissions.AllowAny],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Получение короткой ссылки."""
        recipe = get_object_or_404(Recipe, pk=pk)
        short_url = recipe.short_url
        return Response(
            {
                'short-link': request.build_absolute_uri(
                    f'/{SHORT_LINK_URL_PATH}/{short_url}/'
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        url_path='shopping_cart',
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет рецепт в список покупок или удаляет его."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'error': 'Этот рецепт уже в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            shopping_cart = ShoppingCart.objects.create(
                user=request.user, recipe=recipe
            )
            serializer = ShoppingCartSerializer(
                shopping_cart, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            shopping_cart = ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            )
            if shopping_cart.exists():
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Этот рецепт не в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False, methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Возвращает список покупок в формате PDF."""
        user = request.user
        try:
            ingredients = (
                Ingredient.objects.filter(
                    recipeingredients__recipe__shoppingcarts__user=user
                )
                .values('name', measurement=F('measurement_unit'))
                .annotate(amount=Sum('recipeingredients__amount'))
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        pdf_buffer = generate_pdf(ingredients)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename={PDF_FILENAME}'
        )
        return response

    @action(
        detail=True,
        url_path='favorite',
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавляет рецепт в избранное или удаляет его из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'error': 'Этот рецепт уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite = Favorite.objects.create(
                user=request.user, recipe=recipe
            )
            serializer = FavoriteSerializer(
                favorite, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            favorite = Favorite.objects.filter(
                user=request.user, recipe=recipe
            )
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Этот рецепт не в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )
