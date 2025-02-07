from django.http import JsonResponse
from jestit.serializers.models import GraphSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import objict
from jestit.helpers import logit
from jestit.helpers import modules
from jestit.decorators import http as dec_http

logger = logit.get_logger("debug", "debug.log")
ACTIVE_REQUEST = None

class JestitBase:
    """
    Base model class for REST operations with GraphSerializer integration.
    """

    @property
    def active_request(self):
        return ACTIVE_REQUEST

    @classmethod
    def get_rest_meta_prop(cls, name, default=None):
        if getattr(cls, "RestMeta", None) is None:
            return default
        if isinstance(name, list):
            for n in name:
                res = getattr(cls.RestMeta, n, None)
                if res is not None:
                    return res
            return default
        return getattr(cls.RestMeta, name, default)

    @classmethod
    def rest_error_response(cls, request, status=500, **kwargs):
        payload = dict(kwargs)
        payload["is_authenticated"] = request.user.is_authenticated
        if "code" not in payload:
            payload["code"] = status
        return JsonResponse(payload, status=status)

    @classmethod
    def on_rest_request(cls, request, pk=None):
        """
        Handles REST requests dynamically based on HTTP method.
        """
        cls.__rest_field_names__ = [f.name for f in cls._meta.get_fields()]
        if pk:
            instance = cls.get_instance_or_404(pk)
            if isinstance(instance, dict):  # If it's a response, return early
                return instance

            if request.method == 'GET':
                return cls.on_rest_handle_get(request, instance)

            elif request.method in ['POST', 'PUT']:
                return cls.on_rest_handle_save(request, instance)

            elif request.method == 'DELETE':
                return cls.on_rest_handle_delete(request, instance)
        else:
            return cls.on_handle_list_or_create(request)

        return cls.rest_error_response(request, 500, error=f"{cls.__name__} not found")

    @classmethod
    def get_instance_or_404(cls, pk):
        """Helper method to get an instance or return a 404 response."""
        try:
            return cls.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return cls.rest_error_response(None, 404, error=f"{cls.__name__} not found")

    @classmethod
    def rest_check_permission(cls, request, permission_keys, instance=None):
        """
        Checks permissions using instance-level `has_permission` if available, otherwise falls back to `cls.rest_check_permission`.
        """
        perms = cls.get_rest_meta_prop(permission_keys, [])
        if perms is None or len(perms) == 0:
            return True
        if "all" not in perms:
            if request.user is None or not request.user.is_authenticated:
                return False
        if instance is not None:
            if hasattr(instance, "on_rest_check_permission"):
                return instance.on_rest_check_permission(perms, request)
            if "owner" in perms and getattr(instance, "user", None) is not None:
                if instance.user.id == request.user.id:
                    return True
        if request.group and hasattr(cls, "group"):
            # lets check our group member permissions
            # this will now force any queries to include the group
            return request.group.member_has_permission(request.user, perms)
        return request.user.has_permission(perms)

    @classmethod
    def on_rest_handle_get(cls, request, instance):
        """Handles GET requests with permission checks."""
        if cls.rest_check_permission(request, "VIEW_PERMS", instance):
            return instance.on_rest_get(request)
        return cls.rest_error_response(request, 403, error=f"GET permission denied: {cls.__name__}")

    @classmethod
    def on_rest_handle_save(cls, request, instance):
        """Handles POST and PUT requests with permission checks."""
        if cls.rest_check_permission(request, ["SAVE_PERMS", "VIEW_PERMS"], instance):
            return instance.on_rest_save(request)
        return cls.rest_error_response(request, 403, error=f"{request.method} permission denied: {cls.__name__}")

    @classmethod
    def on_rest_handle_delete(cls, request, instance):
        """Handles DELETE requests with permission checks."""
        if not cls.get_rest_meta_prop("CAN_DELETE", False):
            return cls.rest_error_response(request, 403, error=f"DELETE not allowed: {cls.__name__}")

        if cls.rest_check_permission(request, ["DELETE_PERMS", "SAVE_PERMS", "VIEW_PERMS"], instance):
            return instance.on_rest_delete(request)
        return cls.rest_error_response(request, 403, error=f"DELETE permission denied: {cls.__name__}")

    @classmethod
    def on_rest_handle_list(cls, request):
        if cls.rest_check_permission(request, "VIEW_PERMS"):
            return cls.on_rest_list(request)
        return cls.rest_error_response(request, 403, error=f"GET permission denied: {cls.__name__}")

    @classmethod
    def on_rest_handle_create(cls, request):
        if cls.rest_check_permission(request, ["SAVE_PERMS", "VIEW_PERMS"]):
            instance = cls()
            return instance.on_rest_save(request)
        return cls.rest_error_response(request, 403, error=f"CREATE permission denied: {cls.__name__}")

    @classmethod
    def on_handle_list_or_create(cls, request):
        """Handles listing (GET without pk) and creating (POST/PUT without pk)."""
        if request.method == 'GET':
            return cls.on_rest_handle_list(request)
        elif request.method in ['POST', 'PUT']:
            return cls.on_rest_handle_create(request)

    @classmethod
    def on_rest_list(cls, request, queryset=None):
        """
        Handles listing objects with filtering, sorting, and pagination.
        """
        if queryset is None:
            queryset = cls.objects.all()
        if request.group is not None and hasattr(cls, "group"):
            if "group" in request.DATA:
                del request.DATA["group"]
            queryset = queryset.filter(group=request.group)
        queryset = cls.on_rest_list_filter(request, queryset)
        queryset = cls.on_rest_list_sort(request, queryset)

        # Implement pagination
        page_size = request.DATA.get_typed("size", 10, int)
        page_start = request.DATA.get_typed("start", 0, int)
        page_end = page_start+page_size
        paged_queryset = queryset[page_start:page_end]
        graph = request.DATA.get("graph", "list")
        serializer = GraphSerializer(paged_queryset, graph=graph, many=True)
        return serializer.to_response(request, count=queryset.count(), page=page_start, size=page_size)

    @classmethod
    def on_rest_list_filter(cls, request, queryset):
        """
        Applies filtering logic based on request parameters, including foreign key fields.
        """
        filters = {}
        for key, value in request.GET.items():
            # Split key to check for foreign key relationships
            key_parts = key.split('__')
            field_name = key_parts[0]
            if hasattr(cls, field_name):
                filters[key] = value
            elif field_name in cls.__rest_field_names__ and cls._meta.get_field(field_name).is_relation:
                filters[key] = value
        logger.info("filters", filters)
        return queryset.filter(**filters)


    @classmethod
    def on_rest_list_sort(cls, request, queryset):
        """
        Applies sorting to the queryset.
        """
        sort_field = request.DATA.pop("sort", "-id")
        if sort_field.lstrip('-') in cls.__rest_field_names__:
            return queryset.order_by(sort_field)
        return queryset

    @classmethod
    def on_rest_create(cls, request):
         instance = cls()
         return instance.on_rest_save(request)

    def on_rest_get(self, request):
        """
        Handles retrieving a single object.
        """
        graph = request.GET.get("graph", "default")
        serializer = GraphSerializer(self, graph=graph)
        return serializer.to_response(request)

    def on_rest_save(self, request):
        """
        Creates a model instance from a dictionary.
        """
        data_dict = request.DATA
        for field in self._meta.get_fields():
            field_name = field.name
            if field_name in data_dict:
                field_value = data_dict[field_name]
                set_field_method = getattr(self, f'set_{field_name}', None)
                if callable(set_field_method):
                    set_field_method(field_value, request)
                elif field.is_relation and hasattr(field, 'related_model'):
                    related_model = field.related_model
                    try:
                        related_instance = related_model.objects.get(pk=field_value)
                        setattr(self, field_name, related_instance)
                    except related_model.DoesNotExist:
                        continue  # Skip invalid related instances
                elif field.get_internal_type() == "JSONField":
                    existing_value = getattr(self, field_name, {})
                    logger.info("JSONField", existing_value, "New Value", field_value)
                    if isinstance(field_value, dict) and isinstance(existing_value, dict):
                        merged_value = objict.merge_dicts(existing_value, field_value)
                        logger.info("merged", merged_value)
                        setattr(self, field_name, merged_value)
                else:
                    setattr(self, field_name, field_value)
        self.atomic_save()
        return self.on_rest_get(request)

    def on_rest_delete(self, request):
        """
        Handles deletion of an object.
        """
        try:
            with transaction.atomic():
                self.delete()
            return JsonResponse({"status": "deleted"}, status=204)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def atomic_save(self):
        with transaction.atomic():
            self.save()
