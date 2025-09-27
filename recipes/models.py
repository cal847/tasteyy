from django.db import models
from django.conf import settings
from django.db.models import Avg
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField

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
    category = ArrayField(models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=list))
    api_id = models.PositiveIntegerField(
        help_text="ID from Spoonacular", null=True, blank=True
    )

    diet = ArrayField(models.CharField(max_length=20, choices=DIET_CHOICES, default=list))
    title = models.TextField()
    slug = models.SlugField(unique=True, blank=True, max_length=500)
    description = models.TextField(blank=True, null=True)
    extra_tips = models.TextField(blank=True, null=True)

    servings = models.PositiveIntegerField()
    ingredients = models.TextField(blank=True, null=True)
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
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Recipe.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def avg_rating(self):
        """Calculates the average rating of a recipe and returns as a dictionary"""
        ratings = self.ratings.all()
        return ratings.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0

    def total_ratings(self):
        """Returns the total number of ratings for a recipe"""
        return self.ratings.count()

    def display_category(self):
        """Returns the category in a human readable format eg Main Course instead of ['main course']"""
        if not self.category:
            return "None"
        
        category_map = dict(self.CATEGORY_CHOICES)
        return ",".join([category_map.get(cat, "Unknown") for cat in self.category])
        
    def display_diet(self):
        """Returns the diet in a human readable format eg Main Course instead of ['main course']"""
        if not self.diet:
            return "None"
        
        diet_map = dict(self.DIET_CHOICES)
        return ",".join([category_map.get(cat, "Unknown") for cat in self.diet])

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
