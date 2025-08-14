from django.db import models
from recipes.models import Recipe
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()

class Rating(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(-5)]
                                         )

    def __str__(self):
        return self.rating
    
    def avg_rating(self):
        #calculates the average rating of a recipe and returns as a dictionary
        ratings = self.ratings.all()
        return ratings.aggregate(models.Avg("value"))["value__avg"] or 0
