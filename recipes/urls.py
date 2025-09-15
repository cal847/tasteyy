from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, search_recipes, upload_recipe
from . import views

app_name = 'recipes'

router = DefaultRouter()
router.register(r"", RecipeViewSet)

urlpatterns = [
    path("upload-recipe/", upload_recipe, name="upload-recipe"),

    path("<slug:slug>/", views.recipe_detail, name="recipe_detail"),
    path("", include(router.urls)),
    path("search", search_recipes, name="search"),
]