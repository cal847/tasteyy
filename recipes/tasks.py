import re
import requests
import time
from celery import shared_task
from .models import Recipe, NutritionalValue
from django.conf import settings
from datetime import date
from django.core.cache import cache

API_URL = "https://api.spoonacular.com/recipes/complexSearch"
RECIPE_INFO_URL = "https://api.spoonacular.com/recipes/{id}/information"
API_KEY = settings.SPOONACULAR_API_KEY


@shared_task(bind=True, max_retries=3)
def fetch_recipes(self, offset=0, batch_size=10):
    """Fetches recipes from Spoonacular and saves them into DB"""

    daily_limit = 50

    # Prevent exceeding API call limit
    today = date.today()
    cache_key = f"spoonacular_calls_{today}"

    try:
        calls_used = cache.incr(cache_key)
    except ValueError:
        cache.set(cache_key, 1, 86400)
        calls_used = 1

    if calls_used > daily_limit:
        return f"Daily limit reached: {calls_used}/{daily_limit}"

    params = {
        "apiKey": API_KEY,
        "offset": offset,
        "number": 100,
        "addRecipeNutrition": True,
        "addRecipeInformation": True,
        "sort": "random",
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.HTTPError as exc:
        if response.status_code == 402:
            return f"You have depleted your free API calls. Please upgrade to premium"
        raise self.retry(exc=exc, countdown=30)

    except requests.RequestException as exc:
        raise self.retry(exc=exc, countdown=20)

    data = response.json().get("results", [])

    # Only save recipes with complete information to prevent burning out api calls
    saved_recipes = 0
    for item in data:
        if save_or_update_recipe(item):
            saved_recipes += 1

    print(f"Saved {saved_recipes} out of {len(data)} recipes from offset {offset}.")

    updated_calls = cache.get(cache_key, 0)

    if updated_calls < daily_limit:
        fetch_recipes.apply_async(args=[offset + batch_size], countdown=5)

    return f"Successfully fetched {len(data)} recipes. Calls used: {updated_calls}/{daily_limit}"

def clean_text(text):
    """
    Cleans HTML tags and whitespaces for text formatting
    """
    if not text:
        return ""
    
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)

    # Replace multiple whitespaces with single space
    clean = re.sub(r'\s+', ' ', clean)

    # Remove extra periods and clean up punctuation
    clean = re.sub(r'\.{2,}', '.', clean)

    return clean.strip()

def fetch_detailed_info(recipe_id):
    """
    Fetch detailed recipe information from Spoonacular API.
    The API_URL has limited information such as ingredietns. Therefore, if the info is not available, hit the second url
    """

    # Checks if API calls are still available
    today = date.today()
    cache_key = f"spoonacular_calls_{today}"

    calls_used = cache.get(cache_key, 0)
    daily_limit = 50
    
    if calls_used >= daily_limit:
        print(f"Daily API limit reached, cannot fetch detailed info for recipe {recipe_id}")
        return None
    
    try:
        url = RECIPE_INFO_URL.format(id=recipe_id)
        params = {
            "apiKey": API_KEY,
            "includeNutrition": True
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        time.sleep(0.2)

        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching detailed recipe: {e}")
        return None


def save_or_update_recipe(item):
    """Extract recipe details and save to DB with fallback fetching"""

    recipe_id = item["id"]
    
    # Skip recipe if ingredient is missing
    missing_ingredients = not item.get("extendedIngredients")
    missing_instructions = not item.get("analyzedInstructions") and not item.get("instructions")
    missing_nutrition = "nutrition" not in item
    
    if missing_ingredients or missing_instructions or missing_nutrition:
        print(f"Recipe {recipe_id} missing some information. Attempting to fetch...")

        detailed_info = fetch_detailed_info(recipe_id)

        if detailed_info:
            # Update ingredients if missing
            if missing_ingredients:
                if detailed_info.get("extendedIngredients"):
                    item["extendedIngredients"] = detailed_info["extendedIngredients"]
                    missing_ingredients = False
                    print(f"Found ingredients for recipe {recipe_id}")
            
            # Update instructions if missing
            if missing_instructions:
                if detailed_info.get("analyzedInstructions") or detailed_info.get("instructions"):
                    if detailed_info.get("analyzedInstructions"):
                        item["analyzedInstructions"] = detailed_info["analyzedInstructions"]
                    if detailed_info.get("instructions"):
                        item["instructions"] = detailed_info["instructions"]
                    missing_instructions = False
                    print(f"Found instructions for recipe {recipe_id}")
            
            # Update nutrition if missing
            if missing_nutrition and detailed_info.get("nutrition"):
                item["nutrition"] = detailed_info["nutrition"]
                missing_nutrition = False
                print(f"Found nutrition info for recipe {recipe_id}")
            
            # Update other fields that might be more complete in detailed info
            for field in ["summary", "readyInMinutes", "servings", "image", "title"]:
                if detailed_info.get(field) and (not item.get(field) or len(str(detailed_info[field])) > len(str(item.get(field, "")))):
                    item[field] = detailed_info[field]
        else:
            print("Could not fetch detailed information for {recipe_id}")
    
    # Skip if still missing critical information
    if missing_ingredients or missing_instructions:
        print(f"Skipping recipe {recipe_id}: Still missing critical information after detailed fetch")
        return False 

    # --- Category ---
    category = ["none"]
    for dt in item.get("dishTypes", []):
        if dt.lower() in dict(Recipe.CATEGORY_CHOICES):
            category = [dt.lower()]
            break

    # --- Diet ---
    diet = ["none"]
    for d in item.get("diets", []):
        if d.lower().replace("-", "_") in dict(Recipe.DIET_CHOICES):
            diet = [d.lower().replace("-", "_")]
            break

    # --- Ingredients ---
    raw_ingredients = item.get("extendedIngredients", [])
    if not raw_ingredients:
        raw_ingredients = item.get("usedIngredients", []) + item.get("missedIngredients", [])

    ingredient_texts = [
        (ing.get("original") or ing.get("name") or ing.get("originalString", "")).strip()
        for ing in raw_ingredients if ing
    ]
    ingredients = "\n".join(ingredient_texts) if ingredient_texts else "Ingredients not available."

    # --- Instructions ---
    instructions = []

    analyzed = item.get("analyzedInstructions", [])
    if analyzed and isinstance(analyzed, list):
        for step_group in analyzed:
            for step in step_group.get("steps", []):
                instructions.append(f"{step['number']}. {step['step']}")

    elif item.get("instructions"):
        raw = item["instructions"]
        clean = clean_text(raw)

        # Split by numbered steps if they exist
        if re.search(r'\d+\.', clean):
            steps = re.split(r'(?=\d+\.)', clean)
            instructions = [step.strip() for step in steps if step.strip()]
        else:
            # Split by sentences as fallback
            sentences = re.split(r'(?<=[.!?])\s+', clean)

        instructions = [re.sub(r'^\d+\.\s*', '', inst.strip()) for inst in instructions if inst.strip()]
    else:
        instructions = ["No instructions available."]

    instructions = "\n".join(instructions)

    # --- Clean description ---
    description = clean_text(item.get("summary", ""))

    # --- Save Recipe ---
    recipe, _ = Recipe.objects.update_or_create(
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
            "description": description,
            "author": None,
        },
    )

    # --- Save Nutrition ---
    if "nutrition" in item:
        create_or_update_nutrition(recipe, item["nutrition"])

    return recipe

def create_or_update_nutrition(recipe, nutrition_data):
    """Create or update nutritional data in DB"""
    nutrient_map = {
        item["name"].lower(): item["amount"]
        for item in nutrition_data.get("nutrients", [])
    }

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

    nutritional_value, _ = NutritionalValue.objects.update_or_create(
        recipe=recipe, defaults=defaults
    )

    return nutritional_value
