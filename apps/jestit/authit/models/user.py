from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from jestit.models import JestitBase
import datetime
import uuid

class User(AbstractBaseUser, JestitBase):
    """
    Full custom user model.
    """
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)
    last_activity = models.DateTimeField(default=None, null=True, db_index=True)

    username = models.TextField(unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True, db_index=True)
    display_name = models.CharField(max_length=80, blank=True, null=True, default=None)
    # key used for sessions and general authentication algs
    auth_key = models.TextField(null=True, default=None)
    onetime_code = models.TextField(null=True, default=None)
    # JSON-based permissions field
    permissions = models.JSONField(default=dict, blank=True)
    # JSON-based metadata field
    metadata = models.JSONField(default=dict, blank=True)

    class RestMeta:
        NO_SHOW_FIELDS = ["password", "auth_key", "onetime_code"]
        SEARCH_FIELDS = ["username", "email", "first_name", "last_name", "display_name", "phone_number"]
        VIEW_PERMS = ["view_members", "manage_members", "manage_users", "owner"]
        SAVE_PERMS = ["invite_members", "manage_members", "manage_users", "owner"]
        LIST_DEFAULT_FILTERS = {
            "is_active": True
        }
        UNIQUE_LOOKUP = ["username", "email"]
        GRAPHS = {
            "basic": {
                "fields": [
                    'id',
                    ('get_full_name', 'full_name'),
                    'first_name',
                    'last_name',
                    'display_name',
                    'initials',
                    'username',
                    'email',
                    'phone_number',
                    'last_login',
                    'last_activity',
                    'avatar'
                ]
            },
            "default": {
                "fields": [
                    'id',
                    'uuid',
                    'display_name',
                    ('get_full_name', 'full_name'),
                    'first_name',
                    'last_name',
                    'initials',
                    'username',
                    'email',
                    'phone_number',
                    'is_online',
                    'is_active',
                    'is_blocked',
                    'is_staff',
                    'is_superuser',
                    'requires_totp',
                    'last_login',
                    'last_activity',
                    'password_changed',
                    ('date_joined', 'created'),
                    ("hasLoggedIn", "has_logged_in"),
                    'avatar',
                    'has_totp',
                    'auth_token'
                ],
                "extra": ["metadata", "password_expires_in"],
            },
        }

    def __str__(self):
        return self.email

    def touch(self):
        self.last_activity = datetime.datetime.utcnow()
        self.atomic_save()

    def get_auth_key(self):
        if self.auth_key is None:
            self.auth_key = uuid.uuid4().hex
            self.atomic_save()
        return self.auth_key

    def has_permission(self, perm_key):
        """Check if user has a specific permission in JSON field."""
        if isinstance(perm_key, list):
            for pk in perm_key:
                if pk in self.permissions:
                    return self.permissions.get(pk, False)
            return False
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
