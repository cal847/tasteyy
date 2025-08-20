from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import render
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def home(request):
    return render(request, "base.html")


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    # swagger urls
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # user urls`
    path("api/users/", include("users.urls")),

    # admin urls
    path("api/admin/", include("admin.urls")),

    # recipes urls
    path("api/recipes/", include("recipes.urls")),

    #ratings urls
    path('api/ratings/', include('ratings.urls'))
]
