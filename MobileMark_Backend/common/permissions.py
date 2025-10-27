from rest_framework.permissions import BasePermission

class IsAdminUserRole(BasePermission):
    """
    Custom permission to allow access only to authenticated users with role='Admin'.
    """

    def has_permission(self, request, view):
        user = request.user

        # Must be authenticated
        if not user or not user.is_authenticated:
            return False

        # Must have role = 'Admin'
        return getattr(user, "role", "").strip().lower() == "admin"