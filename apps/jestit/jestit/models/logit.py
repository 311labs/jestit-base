from .base import JestitBase
from django.db import models as dm


class JestitLog(dm.Model, JestitBase):
    created = dm.DateTimeField(auto_now_add=True, db_index=True)
    kind = dm.CharField(max_length=200, default=None, null=True)
    path = dm.TextField(default=None, null=True, db_index=True)
    ip = dm.CharField(max_length=32, default=None, null=True, db_index=True)
    uid = dm.IntegerField(default=0, db_index=True)
    log = dm.TextField(default=None, null=True)
    model_name = dm.TextField(default=None, null=True, db_index=True)
    model_id = dm.IntegerField(default=0, db_index=True)
