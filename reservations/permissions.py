from rest_framework.permissions import BasePermission

from accounts.permissions import IsAdministrator


class ReservationAccessPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            obj.requester_id == request.user.pk
            or IsAdministrator().has_permission(request, view)
        )
