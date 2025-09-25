from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from recipes.views import home
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    
    # swagger urls
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # user urls`
    path("accounts/", include("accounts.urls", namespace='accounts')),

    # admin urls
    path("api/admin/", include("admin.urls")),

    # recipes urls
    path("api/recipes/", include("recipes.urls")),

    #ratings urls
    path('api/ratings/', include('ratings.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)