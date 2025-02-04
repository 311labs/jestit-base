from django.db import models as dm
from jestit.models import JestitBase

class TODO(dm.Model, JestitBase):
    created = dm.DateTimeField(auto_now_add=True)
    modified = dm.DateTimeField(auto_now=True)

    name = dm.CharField(max_length=200, default=None)
    kind = dm.CharField(max_length=200, default=None)
    description = dm.TextField(default=None)
