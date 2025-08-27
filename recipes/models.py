from django.db import models
from django.conf import settings
from django.db.models import Avg
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ("main course", "Main Course"),
        ("side dish", "Side Dish"),
        ("dessert", "Dessert"),
        ("appetizer", "Appetizer"),
        ("salad", "Salad"),
        ("bread", "Bread"),
        ("breakfast", "Breakfast"),
        ("soup", "Soup"),
        ("beverage", "Beverage"),
        ("sauce", "Sauce"),
        ("marinade", "Marinade"),
        ("fingerfood", "Fingerfood"),
        ("snack", "Snack"),
        ("drink", "Drink"),
    ]

    DIET_CHOICES = [
        ("vegan", "Vegan"),
        ("carnivore", "Carnivore"),
        ("gluten_free", "Gluten-free"),
        ("vegetarian", "Vegetarian"),
        ("dairy_free", "Dairy-free"),
        ("none", "None"),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="recipes",
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="none")
    api_id = models.PositiveIntegerField(
        help_text="ID from Spoonacular", null=True, blank=True
    )
    diet = models.CharField(max_length=20, choices=DIET_CHOICES, default="none")
    title = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    servings = models.PositiveIntegerField()
    ingredients = models.TextField()
    image = models.ImageField(upload_to="recipes/", blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    instructions = models.TextField()
    prep_time = models.PositiveIntegerField(default=0)
    cooking_time = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def avg_rating(self):
        """Calculates the average rating of a recipe and returns as a dictionary"""
        ratings = self.ratings.all()
        return ratings.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0

    def total_ratings(self):
        """Returns the total number of ratings for a recipe"""
        return self.ratings.count()


class NutritionalValue(models.Model):
    """Stores nutritional value for each recipe"""

    recipe = models.OneToOneField(
        Recipe, on_delete=models.CASCADE, related_name="nutritional_value"
    )

    # per g
    calories_kcal = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    protein = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    fat = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    carbs = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    fiber = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    sugars = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])

    # micronutrients (mg)
    sodium = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    cholesterol = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    calcium = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    iron = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    vitamin_c = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])

    def __str__(self):
        return f"Nutritional values for {self.recipe}"
