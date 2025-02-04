import json
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.db.models import ForeignKey, OneToOneField
from django.db.models.query import QuerySet

class GraphSerializer:
    """
    Custom serializer for Django models and QuerySets that applies `RestMeta.GRAPHS` dynamically.
    Supports nested relationships and different serialization graphs.
    """

    def __init__(self, instance, graph="default", many=False):
        """
        :param instance: Model instance or QuerySet.
        :param graph: The graph type to use (e.g., "default", "list").
        :param many: Boolean, if `True`, serializes a QuerySet.
        """
        self.graph = graph
        self.qset = None
        # If it's a QuerySet, mark `many=True`
        if isinstance(instance, QuerySet):
            self.many = True
            self.qset = instance
            self.instance = list(instance)  # Convert QuerySet to list for iteration
        else:
            self.many = many
            self.instance = instance

    def serialize(self):
        """
        Serializes a single model instance or a QuerySet.
        """
        if self.many:
            return [self._serialize_instance(obj) for obj in self.instance]
        return self._serialize_instance(self.instance)

    def _serialize_instance(self, obj):
        """
        Serializes a single model instance based on `RestMeta.GRAPHS`.
        """
        if not hasattr(obj, "RestMeta") or not hasattr(obj.RestMeta, "GRAPHS"):
            return model_to_dict(obj)  # Default to `model_to_dict()` if no graph exists

        graph_config = obj.RestMeta.GRAPHS.get(self.graph, {})
        data = model_to_dict(obj)  # Convert normal fields

        # Process extra fields (methods, metadata, etc.)
        extra_fields = graph_config.get("extra", [])
        for field in extra_fields:
            if isinstance(field, tuple):  # Handle renamed method serialization
                method_name, alias = field
            else:
                method_name, alias = field, field

            if hasattr(obj, method_name):
                attr = getattr(obj, method_name)
                data[alias] = attr() if callable(attr) else attr

        # Process related model graphs (ForeignKeys, OneToOneFields)
        related_graphs = graph_config.get("graphs", {})
        for related_field, sub_graph in related_graphs.items():
            related_obj = getattr(obj, related_field, None)

            if related_obj is not None:
                # Determine if the field is a ForeignKey or OneToOneField
                field_obj = obj._meta.get_field(related_field)
                if isinstance(field_obj, (ForeignKey, OneToOneField)):
                    # Serialize related model using its corresponding graph
                    data[related_field] = GraphSerializer(related_obj, graph=sub_graph).serialize()

        return data

    def to_json(self):
        """Returns JSON output of the serialized data."""
        return json.dumps(self.serialize(), cls=DjangoJSONEncoder, indent=4)
