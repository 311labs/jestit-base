from django.db import models as dm
from jestit.models import JestitBase


class TODO(dm.Model, JestitBase):
    created = dm.DateTimeField(auto_now_add=True)
    modified = dm.DateTimeField(auto_now=True)

    name = dm.CharField(max_length=200, default=None)
    kind = dm.CharField(max_length=200, default=None)
    description = dm.TextField(default=None)
    note = dm.ForeignKey(
        "example.Note", null=True, default=None,
        on_delete=dm.CASCADE)

    class RestMeta:
        GRAPHS = {
            "basic": {
                "fields": [
                    'id',
                    'name',
                    'description'
                ]
            },
            "default": {
                "fields": [
                    'id',
                    'name',
                    'kind',
                    'description'
                ],
                "graphs": {
                    "note": "basic"
                }
            }
        }

class Note(dm.Model, JestitBase):
    created = dm.DateTimeField(auto_now_add=True)
    modified = dm.DateTimeField(auto_now=True)

    name = dm.CharField(max_length=200, default=None)
    kind = dm.CharField(max_length=200, default=None)
    description = dm.TextField(default=None)
    password = dm.TextField(default="this is hidden")

    # JSON-based metadata field
    metadata = dm.JSONField(default=dict, blank=True)

    class RestMeta:
        NO_SHOW_FIELDS = ["password"]
        VIEW_PERMS = ["view_notes", "save_notes"]
        SAVE_PERMS = ["save_notes"]
        CAN_DELETE = False
        GRAPHS = {
            "basic": {
                "fields": [
                    'id',
                    'name',
                    'kind',
                    'description'
                ]
            },
            "default": {
                "fields": [
                    'id',
                    'name',
                    'kind',
                    'description',
                    'metadata'
                ]
            }
        }
