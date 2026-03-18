from rest_framework.permissions import BasePermission


# ── role checks ───────

class IsUser(BasePermission):

    message = "Access restricted to users only."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'user'
        )


class IsAdmin(BasePermission):

    message = "Access restricted to admins only."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsSuperAdmin(BasePermission):

    message = "Access restricted to superadmins only."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'superadmin'
        )


class IsAdminOrSuperAdmin(BasePermission):

    message = "Access restricted to admins and superadmins."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'superadmin')
        )


class IsAuthenticatedUser(BasePermission):

    message = "Authentication required."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
