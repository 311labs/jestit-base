import importlib
import os
from django.urls import path, include
from jestit.helpers.settings import settings
from jestit.helpers import modules

JESTIT_API_MODULE = settings.get("JESTIT_API_MODULE", "rest")

urlpatterns = []

def load_jest_modules():
    for app in settings.INSTALLED_APPS:
        module_name = f"{app}.{JESTIT_API_MODULE}"
        print(module_name)
        if not modules.module_exists(module_name):
            continue
        module = modules.load_module(module_name, ignore_errors=False)
        app_module = modules.load_module(app)
        print('loaded')
        if module:
            print(f"loaded: {app}")
            prefix = getattr(module, 'APP_NAME', app)
            if len(prefix) > 1:
                prefix += "/"
            # urls = path(prefix, include(module))
            urls = path(prefix, include(app_module))
            urlpatterns.append(urls)

load_jest_modules()
