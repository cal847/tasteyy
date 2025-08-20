from rest_framework import viewsets, status, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Recipe
from ratings.models import Rating
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RecipeSerializer
from .filters import RecipeFilter
from django.shortcuts import render
from django.http import JsonResponse

User = get_user_model()

def search_recipes(request):
    """
    Renders search queries
    """
    query = request.GET.get("q", "")
    results = []
    if query:
        qs = results = Recipe.objects.filter(title__icontains=query)
        results = list(qs.values("id", "title", "description"))
    return render(request, 'search_list.html')

def recipe_list(self):
    """
    Renders recipes
    """
    queryset = Recipe.objects.all()

    #4 recipes per page
    paginator = Paginator(queryset, 4)

    page_number = request.GET.get("page")
    recipes = paginator.get_page(page_number)

    return render(request, "recipes/recipe_list.html", {"recipes": recipes})

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Determines permissions of users"""
    def has_object_permission(self, request, view, obj):
        #read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        #write permissions only if the user is the owner
        return obj.author == request.user

class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset to handle recipe CRUD"""
    queryset = Recipe.objects.annotate(avg_rating=Avg('ratings__rating'), total_ratings=Count('ratings')).select_related("author", "nutritional_value")
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_permissions(self):
        #viewing(list) open to public
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]

        #other crud 
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
