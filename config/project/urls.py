from django.urls import path, include
from jestit.helpers.settings import settings

JESTIT_PREFIX = "/".join([settings.get("JESTIT_PREFIX", "api/").rstrip("/"), ""])

urlpatterns = [
    path(JESTIT_PREFIX, include('jestit.urls'))
]
