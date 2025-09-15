from rest_framework import viewsets, status, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Recipe
from ratings.models import Rating
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RecipeSerializer
from .filters import RecipeFilter
from .forms import AddRecipeForm
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import redirect

User = get_user_model()

def home(request):
    queryset = Recipe.objects.annotate(avg_rating=Avg("ratings__rating"))

    top_recipes = Recipe.objects.annotate(avg_rating=Avg("ratings__rating")).order_by("-avg_rating")[:4]

    #4 recipes per page
    paginator = Paginator(queryset, 4)

    page_number = request.GET.get("page")
    recipes = paginator.get_page(page_number)

    return render(request, "recipes/recipe_list.html", {"recipes": recipes, "top_recipes": top_recipes})

def search_recipes(request):
    """
    Renders search queries
    """
    query = request.GET.get("q", "")
    results = []
    if query:
        results = Recipe.objects.filter(title__icontains=query)
    return render(request, 'recipes/search_list.html', {"results": results, "query": query})

def recipe_detail(request, slug):
    """
    Renders the details for each recipe
    """
    recipe = get_object_or_404(Recipe, slug=slug)

    nut_v = getattr(recipe, "nutritional_value", None)

    # Split by new lines
    ingredients = recipe.ingredients.split("\n") if recipe.ingredients else []
    instructions = recipe.instructions.split("\n") if recipe.instructions else []

    # Clean up empty strings and whitespace
    ingredients = [ing.strip() for ing in ingredients if ing.strip()]
    instructions = [inst.strip() for inst in instructions if inst.strip()]

    return render(request, "recipes/recipe_detail.html", {"recipe": recipe, "nut_v": nut_v, "ingredients": ingredients, "instructions": instructions},)

def upload_recipe(request):
    """
    Takes user uploads and saves them to the database
    """
    if request.method == 'POST':
        form = AddRecipeForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned = form.cleaned_data
            category = cleaned.get('category', [])
            diet = cleaned.get('diet', [])

            recipe = Recipe.objects.create(
                author=request.user if request.user.is_authenticated else None,
                title=cleaned['title'],
                category=category,
                diet=diet,
                description=cleaned['description'] or "",  # Ensure empty string if None
                ingredients=cleaned['ingredients'],
                instructions=cleaned['instructions'],
                servings=cleaned['servings'],
                cooking_time=cleaned['cooking_time'],
                image=cleaned['image'],
                image_url=None,
                prep_time=cleaned['prep_time'],
            )

            messages.success(request, "Recipe Uploaded Succesfully!")
            return redirect('recipes:recipe_detail', slug=recipe.slug)
        else:
            messages.error(request, "Error:")
    else:
        form = AddRecipeForm()
    
    return render(request, 'recipes/upload_recipe.html', {'form': form})

# def recipe_list(request):
#     """
#     Renders recipes
#     """
    

#     return render(request, "recipes/recipe_list.html", {"recipes": recipes})

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
