import sys
import traceback
from jestit.models import base
from jestit.helpers.settings import settings
from jestit.helpers import modules as jm
from jestit.helpers import logit
import jestit.errors
from django.urls import path, re_path
from django.http import JsonResponse
from functools import wraps
from jestit.helpers.request import parse_request_data

logger = logit.get_logger("jestit", "jestit.log")
logger.info("created")

# Global registry for REST routes
REGISTERED_URLS = {}
URLPATTERN_METHODS = {}
JESTIT_API_MODULE = settings.get("JESTIT_API_MODULE", "api")
JESTIT_APPEND_SLASH = settings.get("JESTIT_APPEND_SLASH", False)


def dispatcher(request, *args, **kwargs):
    """
    Dispatches incoming requests to the appropriate registered URL method.
    """
    base.ACTIVE_REQUEST = request
    key = kwargs.pop('__jestit_key__', None)
    request.DATA = parse_request_data(request)
    logger.info(request.DATA)
    if key in URLPATTERN_METHODS:
        return dispatch_error_handler(URLPATTERN_METHODS[key])(request, *args, **kwargs)
    return JsonResponse({"error": "Endpoint not found", "code": 404}, status=404)


def dispatch_error_handler(func):
    """
    Decorator to catch and handle errors.
    It logs exceptions and returns appropriate HTTP responses.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except jestit.errors.JestitException as err:
            return JsonResponse({"error": err.reason, "code": err.code}, status=err.status)
        except Exception as err:
            logger.exception(f"Unhandled REST Exception: {request.path}")
            stack_trace = traceback.format_exc()
            return JsonResponse({"error": str(err), "stack": stack_trace}, status=500)

    return wrapper


def _register_route(method="ALL"):
    """
    Decorator to automatically register a Django view for a specific HTTP method.
    Supports defining a custom pattern inside the decorator.

    :param method: The HTTP method (GET, POST, etc.).
    """
    def decorator(pattern=None):
        def wrapper(view_func):
            module = jm.get_root_module(view_func)
            if not module:
                print("!!!!!!!")
                print(sys._getframe(2).f_code.co_filename)
                raise RuntimeError(f"Could not determine module for {view_func.__name__}")

            # Ensure `urlpatterns` exists in the calling module
            if not hasattr(module, 'urlpatterns'):
                module.urlpatterns = []

            # If no pattern is provided, use the function name as the pattern
            if pattern is None:
                pattern_used = f"{view_func.__name__}"
            else:
                pattern_used = pattern

            if JESTIT_APPEND_SLASH:
                pattern_used = pattern if pattern_used.endswith("/") else f"{pattern_used}/"

            # Register view in URL mapping
            app_name = module.__name__
            key = f"{module.__name__}__{pattern_used}__{method}"
            print(key)
            URLPATTERN_METHODS[key] = view_func

            # Determine whether to use path() or re_path()
            url_func = path if not (pattern_used.startswith("^") or pattern_used.endswith("$")) else re_path

            # Add to `urlpatterns`
            module.urlpatterns.append(url_func(
                pattern_used, dispatcher,
                kwargs={
                    "__jestit_key__": key
                }))
            # Attach metadata
            view_func.__url__ = (method, pattern_used)
            return view_func
        return wrapper
    return decorator

# Public-facing URL decorators
URL = _register_route()
GET = _register_route("GET")
POST = _register_route("POST")
PUT = _register_route("PUT")
DELETE = _register_route("DELETE")
