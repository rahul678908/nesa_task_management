from django.contrib.auth.models import AbstractUser
from django.db import models


# All possible permissions that can be granted to an Admin
ADMIN_PERMISSION_CHOICES = [
    ('can_create_task',  'Create Tasks'),
    ('can_delete_task',  'Delete Tasks'),
    ('can_view_reports', 'View Completion Reports'),
    ('can_assign_task',  'Assign Tasks to Users'),
]


class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'SuperAdmin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    # Stores a list of permission keys granted to this admin by SuperAdmin.
    # e.g. ["can_create_task", "can_view_reports"]
    # Only meaningful when role == 'admin'. Ignored for other roles.
    admin_permissions = models.JSONField(default=list, blank=True)

    assigned_admin = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'role': 'admin'},
        related_name='assigned_users'
    )

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'superadmin'
        super().save(*args, **kwargs)

    def has_admin_permission(self, perm):
        """Check if this admin has a specific permission key."""
        if self.role == 'superadmin':
            return True  # SuperAdmin always has everything
        return perm in (self.admin_permissions or [])

    def __str__(self):
        return f"{self.username} ({self.role})"
