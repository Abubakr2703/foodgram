from django_filters import rest_framework as filters
from django.db.models import Exists, OuterRef
from recipes.models import Recipe, Favorite, ShoppingCart


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author__id')
    tags = filters.BaseInFilter(field_name='tags__slug', lookup_expr='in')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if value:
            return queryset.filter(favorites__user=user)
        return queryset.exclude(favorites__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if value:
            return queryset.filter(shopping_cart__user=user)
        return queryset.exclude(shopping_cart__user=user)

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']