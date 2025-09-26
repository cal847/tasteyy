from django.db import models
from recipes.models import Recipe
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    @property
    def depth(self):
        """
        Calculate nesting depth (0 = top-level, 1 = reply, etc.)
        Helps with indentation in templates
        """
        depth = 0
        obj = self
        while obj.parent:
            depth += 1
            obj = obj.parent
        return depth

    @property
    def is_reply(self):
        return self.parent is not None

    def __str__(self):
        return f"Comment by {self.author.username}"
