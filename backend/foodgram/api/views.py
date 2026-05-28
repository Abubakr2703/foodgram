from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from recipes.models import (
    Tag,
    Favorite,
    Recipe,
    Ingredient,
    Subscription,
    ShoppingCart
)

from .serializers import (
    TagSerializer,
    RecipeSerializer,
    RecipeWriteSerializer,
    IngredientSerializer,
    RecipeShortSerializer,
    UserProfileSerializer,
    SubscriptionSerializer,
    SubscribeCreateSerializer
)

from .permissions import IsAuthorOrReadOnly

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny,]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeWriteSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        params = self.request.query_params
        user = self.request.user

        if params.get('author'):
            queryset = queryset.filter(author_id=params['author'])
        if tags := params.getlist('tags'):
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        if user.is_authenticated:
            if params.get('is_favorited') == '1':
                queryset = queryset.filter(favorites__user=user)
            elif params.get('is_favorited') == '0':
                queryset = queryset.exclude(favorites__user=user)

            if params.get('is_in_shopping_cart') == '1':
                queryset = queryset.filter(shopping_cart__user=user)
            elif params.get('is_in_shopping_cart') == '0':
                queryset = queryset.exclude(shopping_cart__user=user)

        return queryset

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            _, created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response({'detail': 'Рецепт уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeShortSerializer(
                recipe, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            deleted, _ = Favorite.objects.filter(
                user=request.user, recipe=recipe).delete()
            if not deleted:
                return Response({'detail': 'Рецепт не в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            _, created = ShoppingCart.objects.get_or_create(
                user=request.user, recipe=recipe)
            if not created:
                return Response({'detail': 'Рецепт уже в корзине'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeShortSerializer(
                recipe, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            deleted, _ = ShoppingCart.objects.filter(user=request.user,
                                                     recipe=recipe).delete()
            if not deleted:
                return Response({'detail': 'Рецепт не в корзине'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f'/s/{recipe.id}')
        return Response({'short-link': short_link})

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        cart_items = ShoppingCart.objects.filter(
            user=user).select_related('recipe')
        ingredients = {}
        for cart in cart_items:
            for ri in cart.recipe.recipe_ingredients.all():
                key = f'{ri.ingredient.name}({ri.ingredient.measurement_unit})'
                ingredients[key] = ingredients.get(key, 0) + ri.amount
        lines = ['Список покупок:\n'] + [
            f"- {name} — {amount}" for name, amount in ingredients.items()]
        response = Response('\n'.join(lines), content_type='text/plain')
        response['Content-Disposition'] = 'attachment;'
        'filename="shopping_list.txt"'
        return response


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserProfileSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset.order_by('id'))
        limit = request.query_params.get('recipes_limit', 3)
        serializer = SubscriptionSerializer(
            page or queryset,
            many=True,
            context={'request': request, 'recipes_limit': limit})
        return (
            self.get_paginated_response(serializer.data)
            if page
            else Response(serializer.data)
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """Подписаться на пользователя"""
        author = self.get_object()
        serializer = SubscribeCreateSerializer(
            data={'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserProfileSerializer(
            author,
            context={'request': request}).data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        author = self.get_object()
        deleted, _ = Subscription.objects.filter(
            user=request.user, author=author).delete()
        if not deleted:
            return Response({'detail': 'Вы не подписаны'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
