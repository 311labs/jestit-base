from django.db import models
from jestit.models import JestitBase


class Group(models.Model, JestitBase):
    """
    Group model.
    """
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True, db_index=True)
    kind = models.CharField(max_length=80, default="group", db_index=True)

    parent = models.ForeignKey("authit.Group", null=True, related_name="groups",
        default=None, on_delete=models.CASCADE)

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
                    'kind',
                ]
            },
            "default": {
                "fields": [
                    'id',
                    'name',
                    'created',
                    'modified',
                    'is_active',
                    'kind',
                    'parent',
                    'metadata'
                ]
            },
            "graphs": {
                "parent": "basic"
            }
        }

    def __str__(self):
        return self.name

    def get_member_for_user(self, user):
        from authit.models.member import GroupMember
        return GroupMember.objects.filter(user=user).last()
