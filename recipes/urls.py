from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, search_recipes

app_name = 'recipes'

router = DefaultRouter()
router.register(r"", RecipeViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("search", search_recipes, name="search")
]
