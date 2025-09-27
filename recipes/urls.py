from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RecipeViewSet, search_recipes, upload_recipe, recipe_detail,
    edit_recipe, delete_recipe, add_comment, delete_comment, rate_recipe
)
from .views import RecipeViewSet, search_recipes

app_name = 'recipes'

router = DefaultRouter()
router.register(r"", RecipeViewSet)

urlpatterns = [
    path("upload-recipe/", upload_recipe, name="upload-recipe"),
    path("recipe/<slug:slug>/edit/", edit_recipe, name="edit_recipe"),
    path("recipe/<slug:slug>/delete/", delete_recipe, name="delete_recipe"),
    path("recipe/<slug:slug>/rate/", rate_recipe, name="rate_recipe"),


    # Comments
    path("recipe/<slug:slug>/comment/", add_comment, name="add_comment"),
    path("recipe/<slug:slug>/comment/<int:parent_id>/reply/", add_comment, name="add_reply"),
    path("recipe/<slug:slug>/comment/<int:comment_id>/delete/", delete_comment, name="delete_comment"),

    path("<slug:slug>/", recipe_detail, name="recipe_detail"),
    path("", include(router.urls)),
    path("search", search_recipes, name="search"),
]
