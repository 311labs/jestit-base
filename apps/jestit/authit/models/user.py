from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class User(AbstractBaseUser):
    """
    Full custom user model.
    """
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True)

    username = models.CharField(unique=True, max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    display_name = models.CharField(max_length=80, blank=True, null=True)

    # JSON-based permissions field
    permissions = models.JSONField(default=dict, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_permission(self, perm_key):
        """Check if user has a specific permission in JSON field."""
        return self.permissions.get(perm_key, False)

    def add_permission(self, perm_key, value=True):
        """Dynamically add a permission."""
        self.permissions[perm_key] = value
        self.save()

    def remove_permission(self, perm_key):
        """Remove a permission."""
        if perm_key in self.permissions:
            del self.permissions[perm_key]
            self.save()
