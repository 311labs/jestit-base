from jestit import decorators as jd
from django.http import JsonResponse
from authit.models.group import Group
import datetime

@jd.URL('group')
@jd.URL('group/<int:pk>')
def on_group(request, pk=None):
    return Group.on_rest_request(request, pk)
