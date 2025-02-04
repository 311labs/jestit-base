from django.http import JsonResponse
from jestit.serializers.models import GraphSerializer
from jestit.helpers.request import parse_request_data
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

class JestitBase:
    """
    Base model class for REST operations with GraphSerializer integration.
    """
    @classmethod
    def on_rest_request(cls, request, pk=None):
        """
        Handles REST requests dynamically based on HTTP method.
        """
        request.DATA = parse_request_data(request)
        if pk:
            try:
                instance = cls.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return JsonResponse({"error": "Instance not found", "code": "not_found"}, status=404)

            if request.method == 'GET':
                return instance.on_rest_get(request)
            elif request.method in ['POST', 'PUT']:
                return instance.on_rest_save(request)
            elif request.method == 'DELETE':
                return instance.on_rest_delete(request)
        else:
            if request.method == 'GET':
                return cls.on_rest_list(request)
            elif request.method in ['POST', 'PUT']:
                instance = cls()
                return instance.on_rest_save(request)

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
        return JsonResponse(serializer.serialize(), safe=False)

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
        return JsonResponse(serializer.serialize(), safe=False)

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
                else:
                    setattr(self, field_name, field_value)
        with transaction.atomic():
            self.save()
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
