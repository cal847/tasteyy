from rest_framework import serializers
from .models import Recipe, NutritionalValue

class NutritionalValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionalValue
        fields = [
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
        ]

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""

    author = serializers.StringRelatedField(read_only=True)
    nutritional_value = NutritionalValueSerializer(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "author",
            "category",
            "diet",
            "title",
            "slug",
            "description",
            "servings",
            "ingredients",
            "image",
            "instructions",
            "cooking_time",
            "avg_rating",
            "nutritional_value",
        ]