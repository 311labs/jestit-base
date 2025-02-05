from django.http.response import JsonResponse
from django.urls import path, include
from jestit.helpers.settings import settings

JESTIT_PREFIX = "/".join([settings.get("JESTIT_PREFIX", "api/").rstrip("/"), ""])

urlpatterns = [
    path(JESTIT_PREFIX, include('jestit.urls'))
]


def handler404(request, exception):
    return JsonResponse({"error": "Endpoint not found", "code": 404}, status=404)
