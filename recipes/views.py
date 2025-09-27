from rest_framework import viewsets, status, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Recipe
from ratings.models import Rating
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RecipeSerializer
from .filters import RecipeFilter
from .forms import AddRecipeForm
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import redirect
from comments.forms import CommentForm
from comments.models import Comment
from ratings.models import Rating
from django.template.loader import render_to_string
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator

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

    comments = recipe.comments.select_related('author').order_by('-created_at')
    comment_form = CommentForm()

    # Split by new lines
    ingredients = recipe.ingredients.split("\n") if recipe.ingredients else []
    instructions = recipe.instructions.split("\n") if recipe.instructions else []

    # Clean up empty strings and whitespace
    ingredients = [ing.strip() for ing in ingredients if ing.strip()]
    instructions = [inst.strip() for inst in instructions if inst.strip()]

    return render(request, "recipes/recipe_detail.html", {"recipe": recipe, "nut_v": nut_v, "ingredients": ingredients, "instructions": instructions, "comments": comments, "comment_form": comment_form},)

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

            messages.success(request, "Recipe Uploaded Successfully!")
            return redirect('recipes:recipe_detail', slug=recipe.slug)
        else:
            messages.error(request, "Error:")
    else:
        form = AddRecipeForm()
    
    return render(request, 'recipes/upload_recipe.html', {'form': form})

@login_required
def edit_recipe(request, slug):
    """
    Allows authors to edit their recipes
    """
    recipe = get_object_or_404(Recipe, slug=slug)

    # Ensures only authors can edit
    if recipe.author != request.user:
        return redirect('recipes:recipe_detail', slug=slug)
    
    if request.method == 'POST':
        form = AddRecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            messages.success(request, "Recipe updated successfully")
            return redirect('accounts:profile_view')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = AddRecipeForm(instance=recipe)
    
    return render(request, 'recipes/upload_recipe.html', {
        'form': form,
        'recipe': recipe
    })

@login_required
@require_POST
def delete_recipe(request, slug):
    """
    Allows authors to delete their recipes
    """
    recipe = get_object_or_404(Recipe, slug=slug)

    # Ensures only authors can delete
    if recipe.author != request.user:
        return redirect('recipes:recipe_detail', slug=slug)
    
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, "Recipe deleted successfully")
        return redirect('accounts:profile_view')
    
    return redirect('accounts:profile_view')

@login_required
def add_comment(request, slug, parent_id=None):
    """
    View to add comments, and replies via AJAX.
    If parent_id=None, it becomes a top-level comment else reply.
    """
    recipe = get_object_or_404(Recipe, slug=slug)
    parent = None
    if parent_id:
        parent = get_object_or_404(Comment, id=parent_id, recipe=recipe)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.author = request.user
            comment.parent = parent
            comment.save()

            # Render in HTML fragment
            html = render_to_string("recipes/_comment.html", {"comment": comment}, request=request)
            return JsonResponse({"success": True, "html": html})
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)    

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
        
# @login_required
# def add_reply(request, slug, parent_id):
#     """
#     Refactored in add_reply
#     Allows users to reply to comments
#     """
#     recipe = get_object_or_404(Recipe, slug=slug)
#     parent = get_object_or_404(Comment, id=parent_id, recipe=recipe)
#     if request.method == 'POST':
#         form = ReplyForm(request.POST)
#         if form.is_valid():
#             reply = form.save(commit=False)
#             reply.recipe = recipe
#             reply.author = request.user
#             reply.parent = parent
#             reply.save()
#             messages.success(request, "Reply added!")
#             return redirect("recipe_detail", pk=recipe.id)
#         else:
#             messages.error(request, "Please correct the error below.")
    
#     return redirect('recipes:recipe_detail', slug=slug)

@login_required
def delete_comment(reques, slug, comment_id):
    """
    Allows authors to delete their comments
    """
    recipe = get_object_or_404(Recipe, slug=slug)
    comment = get_object_or_404(Comment, id=comment_id, recipe=recipe)

    if comment.author != request.user:
        return redirect('recipes:recipe_detail', slug=slug)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted!")
        return redirect('recipes:recipe_detail', slug=slug)
    
    return redirect('recipes:recipe_detail', slug=slug)

@login_required
def rate_recipe(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)

    if request.method == "POST":
        value = request.POST.get("rating")
        try:
            value = int(value)
            if value < -5 or value > 5:
                raise ValueError("Invalid rating value")

            # Update if user already rated, otherwise create new
            rating, created = Rating.objects.update_or_create(
                recipe=recipe,
                user=request.user,
                defaults={"value": value},
            )

            if created:
                messages.success(request, f"You rated {recipe.title} with {value}.")
            else:
                messages.success(request, f"Your rating for {recipe.title} was updated to {value}.")

        except (ValueError, TypeError):
            messages.error(request, "Invalid rating. Please pick between -5 and 5.")

    return redirect("recipes:recipe_detail", slug=recipe.slug)
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
