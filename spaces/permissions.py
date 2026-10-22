from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.permissions import IsAdministrator


class AdministratorOrAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.method in SAFE_METHODS or IsAdministrator().has_permission(
            request,
            view,
        )
