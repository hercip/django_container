import json

from rest_framework.utils import serializer_helpers
from rest_framework_addons.serializers import NestedObject
from django.utils.translation import check_for_language
from rest_framework import viewsets


# class NestedModelViewSet(viewsets.ModelViewSet):
#     def list(self, request):
#         return super().list(request)

#     def create(self, request):
#         return super().create(request)

#     def retrieve(self, request, pk=None):
#         return super().retrieve(request, pk)

#     def update(self, request, pk=None):
#         return super().update(request, pk)

#     def partial_update(self, request, pk=None):
#         return super().partial_update(request, pk)

#     def destroy(self, request, pk=None):
#         return super().destroy(request, pk)

#     def perform_destroy(self, instance) -> None:
#         self.serializer_class().delete(instance)


class MultiSerializerModelViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super(MultiSerializerModelViewSet, self).get_serializer_class()

