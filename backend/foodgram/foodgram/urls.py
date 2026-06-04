from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('s/<int:recipe_id>/',
         RedirectView.as_view(url='/recipes/%(recipe_id)s/', permanent=False)),
    path("api/", include("api.urls")),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.authtoken")),
]
