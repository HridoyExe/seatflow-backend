from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, "role", None) == "ADMIN"
        )

class IsAuthenticatedUser(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user

        return False