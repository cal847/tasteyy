from django.contrib import admin
from .models import Recipe, NutritionalValue


class NutritionalValueInline(admin.StackedInline):
    """Inline display of Nutritional Values inside Recipe admin"""
    model = NutritionalValue
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "image_url",
        "author",
        "category",
        "diet",
        "servings",
        "created_at",
        "updated_at",
        "avg_rating_display",
        "total_ratings",
    )
    list_filter = ("category", "diet", "created_at", "updated_at")
    search_fields = ("title", "description", "ingredients")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [NutritionalValueInline]

    def avg_rating_display(self, obj):
        return round(obj.avg_rating(), 2)
    avg_rating_display.short_description = "Avg Rating"


@admin.register(NutritionalValue)
class NutritionalValueAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "calories_kcal",
        "protein",
        "fat",
        "carbs",
        "fiber",
        "sugars",
        "sodium",
        "cholesterol",
        "calcium",
        "iron",
        "vitamin_c",
    )
    search_fields = ("recipe__title",)
