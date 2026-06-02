from api.filters import RecipeFilter
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)
from djoser.serializers import UserCreateSerializer

from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User

from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    SubscribeCreateSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserProfileSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ["^name"]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeSerializer
        return RecipeWriteSerializer

    def _toggle_relation(
        self, request, pk, model, serializer_class=RecipeShortSerializer
    ):
        recipe = self.get_object()
        if request.method == "POST":
            _, created = model.objects.get_or_create(
                user=request.user,
                recipe=recipe)
            if not created:
                return Response(
                    {"detail": "Рецепт уже добавлен"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = serializer_class(
                recipe,
                context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            deleted, _ = model.objects.filter(user=request.user,
                                              recipe=recipe).delete()
            if not deleted:
                return Response(
                    {"detail": "Рецепт не найден"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self._toggle_relation(request, pk, Favorite)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        return self._toggle_relation(request, pk, ShoppingCart)

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f"/s/{recipe.id}")
        return Response({"short-link": short_link})

    @action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart",
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects.filter(recipe__shopping_cart__user=user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )
        lines = ["Список покупок:\n"]
        for item in ingredients:
            name = item["ingredient__name"]
            unit = item["ingredient__measurement_unit"]
            ingr = f"{name}({unit})"
            lines.append(f"- {ingr} — {item['total_amount']}")
        response = Response("\n".join(lines), content_type="text/plain")
        response["Content-Disposition"] = (
            "attachment;"
            'filename="shopping_list.txt"'
        )
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
            UserProfileSerializer(user, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        """Возвращает профиль текущего пользователя"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False, methods=["get"],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset.order_by("id"))
        limit = request.query_params.get("recipes_limit", 3)
        serializer = SubscriptionSerializer(
            page or queryset,
            many=True,
            context={"request": request, "recipes_limit": limit},
        )
        return (
            self.get_paginated_response(serializer.data)
            if page
            else Response(serializer.data)
        )

    @action(
        detail=True, methods=["post"],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """Подписаться на пользователя"""
        author = self.get_object()
        serializer = SubscribeCreateSerializer(
            data={"author": author.id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            UserProfileSerializer(author, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        author = self.get_object()
        deleted, _ = Subscription.objects.filter(
            user=request.user, author=author
        ).delete()
        if not deleted:
            return Response(
                {"detail": "Вы не подписаны"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
