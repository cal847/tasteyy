import requests
from celery import shared_task
from .models import Recipe, NutritionalValue
from django.conf import settings
from django.utils import timezone
from datetime import date
from django.core.cache import cache

API_URL = "https://api.spoonacular.com/recipes/complexSearch"
API_KEY = settings.SPOONACULAR_API_KEY

@shared_task(bind=True, max_retries=3)
def fetch_recipes(self, offset=0, batch_size=10):
    """Fetches recipes from api until their recipes matches our database"""

    recipes_per_call = 100
    daily_limit = 50

    #prevent reaching api call limit
    today = date.today()
    cache_key = f"spoonacular_calls_{today}"
    
    # atomic increment before request
    try:
        calls_used = cache.incr(cache_key, ignore_key_check=True)
    except ValueError:
        cache.set(cache_key, 1, 86400)
        calls_used = 1

    if calls_used > daily_limit:
        return f"Daily limit reached: {calls_used}/{daily_limit}"

    params = {
        "apiKey": API_KEY,
        "offset": offset,
        "number": 100,
        "addRecipeInformation": True,
        "includeNutrition": True,
        "sort": "random",
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.HTTPError as exc:

        # Retry only ofr network errors
        if response.status_code == 402:
            return f"Used maxed quotas at {calls_used}/{daily_limit}"
        
        raise self.retry(exc=exc, countdown=30)  # Retry in 30 seconds
    
    except requests.RequestException as exc:
        raise self.retry(exc=exc, countdown=20)

    # get the data from request
    data = response.json().get("results", [])

    for item in data:
        #save the recipe
        recipe = save_or_update_recipe(item)
        
        if "nutrition" in item:
            create_or_update_nutrition(recipe, item["nutrition"])

    print(f"Fetched {len(data)} recipes from offset {offset}.")

    #check if we've reached the limit
    updated_calls = cache.get(cache_key, 0)

    if updated_calls > daily_limit:
        print(f"Reached daily limit of {daily_limit} calls. Stopping for today.")
    else:
        
        #run the task again if calls is less than limit
        fetch_recipes.apply_async(args=[offset + batch_size], countdown=5)
        
    return f"Successfully fetched {len(data)} recipes. Daily limit reached: {updated_calls}/{daily_limit}"

def save_or_update_recipe(item):
    """
    Extracts the recipe details and updates or creates in DB
    """
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

    # Ingredients
    raw_ingredients = item.get("extendedIngredients", [])
    ingredient_texts = []

    if not raw_ingredients:
        # Fallback: used/missed from search result
        used = item.get("usedIngredients", [])
        missed = item.get("missedIngredients", [])
        raw_ingredients = used + missed

    for ing in raw_ingredients:
        text = ing.get("original") or ing.get("name") or ing.get("originalString")
        if text:
            ingredient_texts.append(text.strip())

    ingredients = "\n".join(ingredient_texts) if ingredient_texts else "Ingredients not available."

    # Instructions
    instructions = []

    analyzed = item.get("analyzedInstructions", [])
    if analyzed and isinstance(analyzed, list):
        for step_group in analyzed:
            for step in step_group.get("steps", []):
                instructions.append(f"{step['number']}. {step['step']}")

    elif item.get("instructions"):
        import re
        raw = item["instructions"]
        clean = re.sub(r'<[^>]+>', '', raw)  # Strip HTML
        lines = [line.strip() for line in clean.split("\n") if line.strip()]
        instructions = [f"{i+1}. {line}" for i, line in enumerate(lines)]
    else:
        instructions = ["No instructions available."]

    instructions = "\n".join(instructions)

    # create or update recipe
    recipe, created = Recipe.objects.update_or_create(
        api_id=item["id"],
        defaults={
            "title": item.get("title"),
            "category": category,
            "diet": diet,
            "cooking_time": item.get("readyInMinutes", 0),
            "image_url": item.get("image"),
            "ingredients": ingredients,
            "servings": item.get("servings", 0),
            "instructions": instructions,
            "description": item.get("summary", ""),
            "author": None,
        },
    )

    return recipe


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
