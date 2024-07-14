from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (
    User,
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart
)
from .serializers import (
    UserCreateSerializer,
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


class UserViewSet(DjoserUserViewSet):

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

    @action(
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
        return Response(status=status.HTTP_204_NO_CONTENT)

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


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    permission_classes = [ReadOnlyOrIsAuthenticatedOrAuthor]

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by('-pub_date')
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__id__in=tags).distinct()
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    #def perform_update(self, serializer):
        #serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        return Response(
            {'link': f'/recipes/{recipe.pk}/'}, status=status.HTTP_200_OK
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
        user = request.user
        shopping_cart = user.shopping_cart.all()
        # Generate and return the shopping cart file content as needed
        return Response({'status': 'Download shopping cart'}, status=status.HTTP_200_OK)

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
