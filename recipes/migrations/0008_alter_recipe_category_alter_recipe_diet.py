# recipes/migrations/0008_alter_recipe_category_alter_recipe_diet.py
import django.contrib.postgres.fields
from django.db import migrations, models


# 👇 DEFINED BEFORE IT'S USED — THIS IS CRITICAL!
def copy_and_clean_data(apps, schema_editor):
    Recipe = apps.get_model('recipes', 'Recipe')
    
    for recipe in Recipe.objects.all():
        # Clean category
        if isinstance(recipe.category, str) and recipe.category == "none":
            recipe.category_temp = []
        elif isinstance(recipe.category, list):
            recipe.category_temp = [item for item in recipe.category if item != "none"]
        else:
            recipe.category_temp = []

        # Clean diet
        if isinstance(recipe.diet, str) and recipe.diet == "none":
            recipe.diet_temp = []
        elif isinstance(recipe.diet, list):
            recipe.diet_temp = [item for item in recipe.diet if item != "none"]
        else:
            recipe.diet_temp = []

        # Save only if changed
        recipe.save(update_fields=['category_temp', 'diet_temp'])


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0007_rename_tips_recipe_extra_tips"),
    ]

    operations = [
        # Step 1: Add temporary fields to hold cleaned data
        migrations.AddField(
            model_name="recipe",
            name="category_temp",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    max_length=20,
                    choices=[
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
                    ],
                ),
                blank=True,
                null=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="diet_temp",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    max_length=20,
                    choices=[
                        ("vegan", "Vegan"),
                        ("carnivore", "Carnivore"),
                        ("gluten_free", "Gluten-free"),
                        ("vegetarian", "Vegetarian"),
                        ("dairy_free", "Dairy-free"),
                        ("none", "None"),
                    ],
                ),
                blank=True,
                null=True,
                default=list,
                size=None,
            ),
        ),

        # Step 2: Copy and clean existing data from old fields to temp fields
        migrations.RunPython(copy_and_clean_data),  # ✅ Now this works!

        # Step 3: Remove the old broken fields
        migrations.RemoveField(
            model_name="recipe",
            name="category",
        ),
        migrations.RemoveField(
            model_name="recipe",
            name="diet",
        ),

        # Step 4: Rename temp fields to real names
        migrations.RenameField(
            model_name="recipe",
            old_name="category_temp",
            new_name="category",
        ),
        migrations.RenameField(
            model_name="recipe",
            old_name="diet_temp",
            new_name="diet",
        ),
    ]