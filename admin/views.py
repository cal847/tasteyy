from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .serializers import AdminUserSerializer
from django.contrib.auth import get_user_model
from rest_framework.decorators import action


User = get_user_model()

class AdminUserViewSet(viewsets.ViewSet):
    """
    Admin-only viewset for managing users
    """
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'], url_path='list')
    def list_users(self, request):
        """List all users"""
        users = User.objects.all()
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='promote')
    def promote(self, request, pk=None):
        """Promote user to admin"""
        user = get_object_or_404(User, pk=pk)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return Response(
            {"message": f"{user.username}, {user.email} is now an admin"}
            )

    @action(detail=True, methods=['post'], url_path='demote')
    def demote(self,request, pk=None):
        """Demote user from admin"""
        user = get_object_or_404(User, pk=pk)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        return Response(
            {"message": f"{user.username}, {user.email} is no longer an admin"}
            )

    def destroy(self, request, pk=None):
        """Delete a User"""
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response({"message": "User deleted successfully"})
