from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from jestit.models import JestitBase
from jestit.helpers.settings import settings
from jestit import errors as jerrors
import datetime
import uuid

USER_PERMS_PROTECTION = settings.get("USER_PERMS_PROTECTION", {})

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
        VIEW_PERMS = ["view_users", "manage_users", "owner"]
        SAVE_PERMS = ["manage_users", "owner"]
        LIST_DEFAULT_FILTERS = {
            "is_active": True
        }
        UNIQUE_LOOKUP = ["username", "email"]
        GRAPHS = {
            "basic": {
                "fields": [
                    'id',
                    'display_name',
                    'username',
                    'email',
                    'phone_number',
                    'last_login',
                    'last_activity'
                ]
            },
            "default": {
                "fields": [
                    'id',
                    'display_name',
                    'username',
                    'email',
                    'phone_number',
                    'last_login',
                    'last_activity',
                    'permissions',
                    'metadata'
                ],
            },
        }

    def __str__(self):
        return self.email

    def is_request_user(self, request=None):
        if request is None:
            request = self.active_request
        if request is None:
            return False
        return request.user.id == self.id

    def touch(self):
        self.last_activity = datetime.datetime.utcnow()
        self.atomic_save()

    def get_auth_key(self):
        if self.auth_key is None:
            self.auth_key = uuid.uuid4().hex
            self.atomic_save()
        return self.auth_key

    def set_permissions(self, value, request):
        if not isinstance(value, dict):
            return
        for key in value:
            if key in USER_PERMS_PROTECTION:
                if not request.user.has_permission(USER_PERMS_PROTECTION[key]):
                    raise jerrors.PermissionDeniedException()
            elif not request.user.has_permission("manage_users"):
                raise jerrors.PermissionDeniedException()
            if bool(value[key]):
                self.add_permission(key)
            else:
                self.remove_permission(key)

    def has_permission(self, perm_key):
        """Check if user has a specific permission in JSON field."""
        if isinstance(perm_key, list):
            for pk in perm_key:
                if self.has_permission(pk):
                    return True
            return False
        if perm_key == "all":
            return True
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

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split("@")[0]
        if not self.display_name:
            self.display_name = self.username
        super().save(*args, **kwargs)

    def on_rest_check_permission(self, perms, request):
        if "owner" in perms and self.is_request_user():
            return True
        return request.user.has_permission(perms)
