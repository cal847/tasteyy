import requests
from celery import shared_task
from .models import Recipe, NutritionalValue
from django.conf import settings

API_URL = "https://api.spoonacular.com/recipes/complexSearch"
API_KEY = settings.SPOONACULAR_API_KEY


@shared_task(bind=True, max_retries=3)
def fetch_recipes(self, offset=0, batch_size=10):
    """Fetches recipes from api until their recipes matches our database"""

    params = {
        "apiKey": API_KEY,
        "offset": offset,
        "number": batch_size,
        "addRecipeInformation": True,
        "includeNutrition": True,
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        total_api_recipes = response.json().get("total", 0)

        my_recipes = Recipe.objects.count()

        # get the data from request
        data = response.json().get("results", [])

        for item in data:
            # extract categories
            category = "none"
            for dt in item.get("dishTypes", []):
                if dt.lower() in dict(Recipe.CATEGORY_CHOICES):
                    category = dt.lower()
                    break

            # extract diet
            diet = "none"
            for d in item.get("diets", []):
                if d.lower().replace("-", "_") in dict(Recipe.DIET_CHOICES):
                    diet = d.lower().replace("-", "_")
                    break

            # format ingredients as plain text
            ingredients = "\n".join(
                [ing["original"] for ing in item.get("extendedIngredients", [])]
            )

            # format instructions as plain text
            instructions = []
            for instr in item.get("analyzedInstructions", []):
                for step in instr.get("steps", []):
                    instructions.append(f"{step['number']}. {step['step']}")
            instructions = "\n".join(instructions)

            # creat or update recipe
            recipe, created = Recipe.objects.update_or_create(
                api_id=item["id"],
                defaults={
                    "title": item.get("title"),
                    "category": category,
                    "diet": diet,
                    "cooking_time": item.get("readyInMinutes", 0),
                    "image": item.get("image"),
                    "ingredients": ingredients,
                    "servings": item.get("servings", 0),
                    "instructions": instructions,
                    "description": item.get("summary", "")[:500],
                    "author": None,
                },
            )

            if "nutrition" in item:
                create_or_update_nutrition(recipe, item["nutrition"])

            print(f"Fetched {len(data)} recipes from offset {offset}.")

            # schedule after 12 minutes
            fetch_recipes.apply_async(
                kwargs={"offset": offset + batch_size, "batch_size": batch_size},
                countdown=60 * 12,
            )

    except requests.RequestException as exc:
        print(f"Request failed: {exc}")
        raise self.retry(exc=exc, countdown=60 * 15)  # Retry in 15 mins


def create_or_update_nutrition(recipe, nutrition_data):
    """Function to create or update nutritional data in my database"""
    nutrient_map = {
        item["name"].lower(): item["amount"]
        for item in nutrition_data.get("nutrients", [])
    }

    # map to my model fields
    defaults = {
        "calories_kcal": nutrient_map.get("calories", 0.0),
        "protein": nutrient_map.get("protein", 0.0),
        "fat": nutrient_map.get("fat", 0.0),
        "carbs": nutrient_map.get("carbohydrates", 0.0),
        "fiber": nutrient_map.get("fiber", 0.0),
        "sugars": nutrient_map.get("sugar", 0.0),
        "sodium": nutrient_map.get("sodium", 0.0),
        "cholesterol": nutrient_map.get("cholesterol", 0.0),
        "calcium": nutrient_map.get("calcium", 0.0),
        "iron": nutrient_map.get("iron", 0.0),
        "vitamin_c": nutrient_map.get("vitamin c", 0.0),
    }

    nutritional_value, created = NutritionalValue.objects.update_or_create(
        recipe=recipe, defaults=defaults
    )

    return nutritional_value, created
