from rest_framework.serializers import serializers
from .models import Rating
from django.contrib.auth import get_user_model
from recipes.models import Recipe

class RatingSerializer(serializers.ModelSerializer):
    recipe = serializers.CharField(source='recipe.title', read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = ["id", "user", "user_id", "recipe", "rating", "comment", "created_at", "updated_at",  "average_rating"]

    def get_average_rating(self, obj):
        return round(obj.avg_rating, 1) if avg_rating else None
