from jestit.decorators import http as jd
from django.http import JsonResponse
from example.models import TODO, Note


@jd.URL('todo')
@jd.URL('todo/<int:pk>')
def on_todo(request, pk=None):
    return TODO.on_rest_request(request, pk)


@jd.URL('note')
@jd.URL('note/<int:pk>')
def on_note(request, pk=None):
    return Note.on_rest_request(request, pk)
