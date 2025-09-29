from django.db import models
from recipes.models import Recipe
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()


class Rating(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ratings")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default= 0.0,
        blank=True,
        null=True,
        validators=[MaxValueValidator(5), MinValueValidator(-5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("author", "recipe")

    def __str__(self):
        return f"{self.rating}"
