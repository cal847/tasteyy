from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .serializers import RatingSerializer
from .models import Rating
from recipes.models import Recipe
from django.contrib.auth import get_user_model
from .permissions import IsOwnerOrReadOnly

User = get_user_model()

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.select_related('recipe').all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def create(self, request, *args, **kwargs):
        """Lets a user to rate and review a recipe or update an existing one"""
        recipe_id = request.data.get("recipe")
        existing_rating = Rating.objects.filter(user=request.user, recipe_id=recipe_id).first()

        #updates existing rating 
        if existing_rating:
            serializer = self.get_serializer(
                    existing_rating, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        #create a new rating
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
