from django.http import JsonResponse
from jestit.serializers.models import GraphSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import objict
from jestit.helpers import logit

logger = logit.get_logger("debug", "debug.log")


class JestitBase:
    """
    Base model class for REST operations with GraphSerializer integration.
    """

    @classmethod
    def rest_check_permission(cls, request, perms):
        """
        Check if request user has one of the required permissions.
        """
        if perms is None or len(perms) == 0:
            return True
        if request.user is None or not request.user.is_authenticated:
            return False
        return request.user.has_permission(perms)

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
        if pk:
            try:
                instance = cls.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return cls.rest_error_response(request, 404, error=f"{cls.__name__} not found")

            if request.method == 'GET':
                if cls.rest_check_permission(request, cls.get_rest_meta_prop("VIEW_PERMS", [])):
                    return instance.on_rest_get(request)
                return cls.rest_error_response(request, 403, error=f"{request.method} permission denied: {cls.__name__}")

            elif request.method in ['POST', 'PUT']:
                if cls.rest_check_permission(request, cls.get_rest_meta_prop(["SAVE_PERMS", "VIEW_PERMS"], [])):
                    return instance.on_rest_save(request)
                return cls.rest_error_response(request, 403, error=f"{request.method} permission denied: {cls.__name__}")

            elif request.method == 'DELETE':
                if not cls.get_rest_meta_prop("CAN_DELETE", False):
                    return cls.rest_error_response(request, 403, error=f"{request.method} permission denied: {cls.__name__}")
                if cls.rest_check_permission(request, cls.get_rest_meta_prop(["DELETE_PERMS", "SAVE_PERMS", "VIEW_PERMS"], [])):
                    return instance.on_rest_delete(request)
                return cls.rest_error_response(request, 403, error=f"{request.method} permission denied: {cls.__name__}")
        else:
            if request.method == 'GET':
                if cls.rest_check_permission(request, cls.get_rest_meta_prop("VIEW_PERMS", [])):
                    return cls.on_rest_list(request)
                return cls.rest_error_response(request, 403, error=f"{request.method} permission denied: {cls.__name__}")
            elif request.method in ['POST', 'PUT']:
                if cls.rest_check_permission(request, cls.get_rest_meta_prop(["SAVE_PERMS", "VIEW_PERMS"], [])):
                    instance = cls()
                    return instance.on_rest_save(request)
                return cls.rest_error_response(request, 403, error=f"CREATE permission denied: {cls.__name__}")
        return cls.rest_error_response(request, 500, error=f"{cls.__name__} not found")

    @classmethod
    def on_rest_list(cls, request):
        """
        Handles listing objects with filtering and sorting.
        """
        queryset = cls.objects.all()
        queryset = cls.on_rest_list_filter(request, queryset)
        queryset = cls.on_rest_list_sort(request, queryset)
        print(request.DATA.toJSON(as_string=True))
        graph = request.DATA.get("graph", "list")
        serializer = GraphSerializer(queryset, graph=graph, many=True)
        return serializer.to_response(request)

    @classmethod
    def on_rest_list_filter(cls, request, queryset):
        """
        Applies filtering logic based on request parameters.
        """
        filters = {}
        for key, value in request.GET.items():
            if hasattr(cls, key):
                filters[key] = value
        return queryset.filter(**filters)

    @classmethod
    def on_rest_list_sort(cls, request, queryset):
        """
        Applies sorting to the queryset.
        """
        sort_field = request.GET.get("sort", "-id")
        if sort_field.lstrip('-') in [f.name for f in cls._meta.get_fields()]:
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
                    set_field_method(field_value)
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
