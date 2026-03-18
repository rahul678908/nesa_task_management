from rest_framework.permissions import BasePermission


# ── Hardcoded role checks ──────────────────────────────────────────────────────

class IsUser(BasePermission):
    """Grants access only to regular users (role == 'user')."""
    message = "Access restricted to users only."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'user'
        )


class IsAdmin(BasePermission):
    """Grants access only to admins (role == 'admin')."""
    message = "Access restricted to admins only."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsSuperAdmin(BasePermission):
    """Grants access only to superadmins (role == 'superadmin')."""
    message = "Access restricted to superadmins only."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'superadmin'
        )


class IsAdminOrSuperAdmin(BasePermission):
    """Grants access to admins AND superadmins."""
    message = "Access restricted to admins and superadmins."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'superadmin')
        )


class IsAuthenticatedUser(BasePermission):
    """Grants access to any authenticated user regardless of role."""
    message = "Authentication required."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
