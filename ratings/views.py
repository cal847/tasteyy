from rest_framework import viewsets, status, permissions, action
from .serializers import RatingSerializer
from .models import Rating
from recipes.models import Recipe
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.select_related('recipe').all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'put'], url_path='my_rating')
    def my_rating(self, request, *args, **kwargs):
        """
        GET: Get my rating for this recipe
        PUT: Create or update my rating for this recipe
        URL: /api/recipes/1/my-rating/
        """
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_add)

        #try getting the rating
        rating = Rating.objects.filter(user=request.user, recipe=recipe).first()

        if request.method == 'GET':
            if not rating:
                return Response(
                    {"detail": "You haven't rated this recipe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(rating)
            return Response(serializer.data)

        elif request.method == 'PUT':
            # Prepare data
            data = request.data.copy()
            data['recipe'] = recipe.id  # Enforce recipe from URL

            if rating:
                # Update existing rating
                serializer = self.get_serializer(rating, data=data)
            else:
                # Create new rating
                serializer = self.get_serializer(data=data)

            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)

            return Response(serializer.data, status=status.HTTP_200_OK)
