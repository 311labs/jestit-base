from django.db import models
from jestit.models import JestitBase


class GroupMember(models.Model, JestitBase):
    """
    A member of a group
    """
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, db_index=True)
    user = models.ForeignKey(
        "authit.User",related_name="members",
        on_delete=models.CASCADE)
    group = models.ForeignKey(
        "authit.Group", related_name="members",
        on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, db_index=True)
    # JSON-based permissions field
    permissions = models.JSONField(default=dict, blank=True)
    # JSON-based metadata field
    metadata = models.JSONField(default=dict, blank=True)

    class RestMeta:
        VIEW_PERMS = ["view_groups", "manage_groups"]
        SAVE_PERMS = ["manage_groups"]
        LIST_DEFAULT_FILTERS = {
            "is_active": True
        }
        GRAPHS = {
            "basic": {
                "fields": [
                    'id',
                    'name',
                    'created',
                    'modified',
                    'is_active',
                    'group',
                    'user',
                    'permissions',
                    'metadata'
                ]
            }
        }

    def __str__(self):
        return f"{self.user.username}@{self.group.name}"
