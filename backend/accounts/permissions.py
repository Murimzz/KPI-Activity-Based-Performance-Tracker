from rest_framework.permissions import BasePermission, SAFE_METHODS

from accounts.models import UserRole


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == UserRole.ADMIN or request.user.is_superuser)
        )


class IsSupervisorRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.role in (UserRole.SUPERVISOR, UserRole.ADMIN)
            )
        )


class IsSupervisorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.role in (UserRole.SUPERVISOR, UserRole.ADMIN)
            )
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.is_superuser or user.role == UserRole.ADMIN


class IsOwnerSupervisorOrAdmin(BasePermission):
    """Object-level: assignee, their supervisor, or admin."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.role == UserRole.ADMIN:
            return True

        assigned_to_id = getattr(obj, 'assigned_to_id', None)
        supervisor_id = getattr(obj, 'supervisor_id', None)

        if assigned_to_id == user.id:
            return True
        if supervisor_id == user.id:
            return True
        if hasattr(obj, 'user_id') and obj.user_id == user.id:
            return True
        return False
