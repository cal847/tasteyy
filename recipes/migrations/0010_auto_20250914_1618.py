# recipes/migrations/0010_fix_corrupted_array_fields.py
from django.db import migrations

def fix_corrupted_arrays(apps, schema_editor):
    Recipe = apps.get_model('recipes', 'Recipe')
    
    # Loop through every recipe and fix category/diet fields
    for recipe in Recipe.objects.all():
        changed = False
        
        # Clean category field
        if recipe.category:
            if isinstance(recipe.category, str):
                # If stored as raw string (e.g., '"none"' or '"breakfast"'), convert to list
                # This handles legacy corruption from bad default
                if recipe.category == "none":
                    recipe.category = []
                    changed = True
                else:
                    # Try parsing as JSON-like string? Unlikely, but just in case
                    try:
                        import json
                        parsed = json.loads(recipe.category.replace("'", '"'))
                        if isinstance(parsed, list):
                            recipe.category = [item for item in parsed if item != "none"]
                            changed = True
                    except:
                        # Just clear it if we can't parse
                        recipe.category = []
                        changed = True
            elif isinstance(recipe.category, list):
                # Remove any "none" items from the list
                cleaned = [item for item in recipe.category if item != "none"]
                if cleaned != recipe.category:
                    recipe.category = cleaned
                    changed = True
        
        # Clean diet field (same logic)
        if recipe.diet:
            if isinstance(recipe.diet, str):
                if recipe.diet == "none":
                    recipe.diet = []
                    changed = True
                else:
                    try:
                        import json
                        parsed = json.loads(recipe.diet.replace("'", '"'))
                        if isinstance(parsed, list):
                            recipe.diet = [item for item in parsed if item != "none"]
                            changed = True
                    except:
                        recipe.diet = []
                        changed = True
            elif isinstance(recipe.diet, list):
                cleaned = [item for item in recipe.diet if item != "none"]
                if cleaned != recipe.diet:
                    recipe.diet = cleaned
                    changed = True
        
        # Save only if changes were made
        if changed:
            recipe.save(update_fields=['category', 'diet'])

def reverse_fix(apps, schema_editor):
    # No reverse needed — we’re cleaning up bad data, not restoring it
    pass

class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0009_alter_recipe_category_alter_recipe_diet"),
    ]

    operations = [
        migrations.RunPython(fix_corrupted_arrays, reverse_fix),
    ]