from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from django.http import HttpResponse
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from django.db.models import Sum, F
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart
)
from .serializers import (
    UserSerializer,
    AvatarSerializer,
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    SubscriptionsSerializer
)
from .permissions import ReadOnlyOrIsAuthenticatedOrAuthor
from .mixins import DjoserPermissionsMethodsMixin
from .paginators import PaginatorWithLimit
from foodgram.constants import PDF_FILENAME, SHORT_LINK_URL_PATH
from .filters import RecipeFilter, IngredientFilter
from .utils import generate_pdf


class UserViewSet(DjoserUserViewSet, DjoserPermissionsMethodsMixin):
    pagination_class = PaginatorWithLimit

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            request.user.avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    """@action(
        detail=False,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='set_password'
        )
    def set_password(self, request):
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.data['password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)"""

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        serializer = SubscriptionsSerializer(
            request.user.subscriptions.all(),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, pk=None):
        author = self.get_object()
        if author == request.user:
            return Response(
                {'status': 'Вы не можете подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if request.user.subscriptions.filter(author=author).exists():
                return Response(
                    {'status': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            request.user.subscriptions.create(author=author)
            return Response(
                {'status': 'Вы подписались'}, status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            subscription = request.user.subscriptions.filter(
                author=author
            ).first()
            if not subscription:
                return Response(
                    {'status': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(
                {'status': 'Вы отписались'},
                status=status.HTTP_204_NO_CONTENT
            )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [permissions.AllowAny]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    pagination_class = PaginatorWithLimit
    permission_classes = [ReadOnlyOrIsAuthenticatedOrAuthor]
    filterset_class = RecipeFilter

    @action(
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return Response(
            {
                'short-link': request.build_absolute_uri(
                    f'/{SHORT_LINK_URL_PATH}/{recipe.short_url}/'
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
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
            serializer = ShoppingCartSerializer(shopping_cart)
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
        ingredients = (
            Ingredient.objects.filter(recipe__recipe__in_carts__user=user)
            .values('name', measurement=F('measurement_unit'))
            .annotate(amount=Sum('recipe__amount'))
        )

        pdf_buffer = generate_pdf(ingredients)

        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename={PDF_FILENAME}'
        )
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            if Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'error': 'Этот рецепт уже в списке избранного.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite = Favorite.objects.create(
                user=request.user, recipe=recipe
            )
            serializer = FavoriteSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            favorite = Favorite.objects.filter(
                user=request.user, recipe=recipe
            )
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Этот рецепт не в списке избранного.'},
                status=status.HTTP_400_BAD_REQUEST
            )
