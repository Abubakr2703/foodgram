from django.contrib import admin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import include, path
from recipes.models import Recipe
from recipes.utils import decode_base62


def redirect_to_recipe(request, hash_code):
    try:
        recipe_id = decode_base62(hash_code)
        recipe = Recipe.objects.get(id=recipe_id)
        return redirect(f"/recipes/{recipe.id}")
    except (ValueError, Recipe.DoesNotExist):
        raise Http404("Рецепт не найден")


urlpatterns = [
    path("admin/", admin.site.urls),
    path('s/<str:hash_code>/', redirect_to_recipe, name='short_redirect'),
    path("api/", include("api.urls")),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.authtoken")),
]
