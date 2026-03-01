from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):

        # First ensure user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        # Safe methods allowed for both roles
        if request.method in SAFE_METHODS:
            return request.user.role in ["ADMIN", "REVIEWER"]
        # Write methods only for admin
        return request.user.role == "ADMIN"
