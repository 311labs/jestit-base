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

    def has_permission(self, user):
        from authit.models.member import GroupMember
        return GroupMember.objects.filter(user=user).last()

    def member_has_permission(self, user, perms):
        ms = self.has_permission(user)
        if ms is None:
            return user.has_permission(perms)
        return ms.has_permission(perms)

    @classmethod
    def on_rest_handle_list(cls, request):
        if cls.rest_check_permission(request, "VIEW_PERMS"):
            return cls.on_rest_list(request)
        group_ids = request.user.members.values_list('group__id', flat=True)
        return cls.on_rest_list(request, cls.objects.filter(id__in=group_ids))
