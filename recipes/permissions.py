from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permissions to allow owners of recipes full CRUD operations
    """
    def has_obj_permission(self, request, view, obj):

        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are restricted to owner
        return obj.author == request.user