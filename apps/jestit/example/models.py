from django.db import models as dm
from jestit.models import JestitBase

class TODO(dm.Model, JestitBase):
    created = dm.DateTimeField(auto_now_add=True)
    modified = dm.DateTimeField(auto_now=True)

    name = dm.CharField(max_length=200, default=None)
    kind = dm.CharField(max_length=200, default=None)
    description = dm.TextField(default=None)



class Note(dm.Model, JestitBase):
    created = dm.DateTimeField(auto_now_add=True)
    modified = dm.DateTimeField(auto_now=True)

    name = dm.CharField(max_length=200, default=None)
    kind = dm.CharField(max_length=200, default=None)
    description = dm.TextField(default=None)
    password = dm.TextField(default="this is hidden")

    class RestMeta:
        NO_SHOW_FIELDS = ["password"]
        VIEW_PERMS = ["view_notes", "save_notes"]
        SAVE_PERMS = ["save_notes"]
        CAN_DELETE = False
        GRAPHS = {
            "basic": {
                "fields": [
                    'id',
                    'kind',
                    'description'
                ]
            },
            "default": {
                "fields": [
                    'id',
                    'name',
                ]
            }
        }
