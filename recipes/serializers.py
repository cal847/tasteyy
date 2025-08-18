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
    average_rating = serializers.SerializerMethodField(read_only=True)

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
            "prep_time",
            "cooking_time",
            "average_rating",
            "total_ratings",
            "nutritional_value",
        ]

    def get_avg_rating(self, obj):
        """Returns the average rating for a recipe"""
        return round(obj.avg_rating, 1) if obj.avg_rating else None

    def get_total_ratings(self, obj):
        """Returns the total number of ratings for a recipe"""
        return obj.total_ratings()
