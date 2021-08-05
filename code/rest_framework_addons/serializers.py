from collections import OrderedDict
from typing import Any
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from django.db import models
from django.db.models.fields import files
from django.db.models.query import QuerySet
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict
import sys


class NestedObject(object):
    def __init__(self,
                 field_name: str,
                 serializer_class: any,
                 key_field_name=None,
                 m2m_field=None,
                 many=False,
                 is_o2o=False,
                 is_required=False,
                 is_parent_dependent=False,
                 filter_name=None,
                 filter_method=None) -> None:
        self.field_name = field_name
        self.__serializer_class = serializer_class
        self.key_field_name = key_field_name
        self.m2m_field = m2m_field
        self.is_parent_dependent = is_parent_dependent
        self.is_o2o = is_o2o
        self.is_required = is_required
        self.many = many
        self.filter_name = filter_name
        self.filter_method = filter_method
        self.received_data = None

    @property
    def serializer_class(self) -> type:
        sc = self.__serializer_class
        if isinstance(sc, type):
            return sc
        _package, _class = sc.rsplit('.', 1)
        return getattr(sys.modules[_package], _class)

    @property
    def model(self):
        return self.serializer_class.Meta.model

    def update_or_create_instances(self, key='id', parent=None) -> list:
        def update_or_create_instance(data, parent) -> models.Model:
            def create_model(data) -> models.Model:
                def append_filter_if_required():
                    name = self.field_name
                    if self.filter_method:
                        data[self.filter_name] = self.filter_method(name)

                try:
                    append_filter_if_required()
                    serializer = self.serializer_class(data=data)
                    serializer.is_valid(raise_exception=True)
                    instance = self.serializer_class().create(
                        serializer.validated_data)
                except IntegrityError as e:
                    raise SuspiciousOperation(f"Creating {self.model} falied.")
                return instance

            def update_model(data) -> models.Model:
                instance = self.instance_of_pk(data[key])
                try:
                    serializer = self.serializer_class(instance=instance,
                                                       data=data)
                    serializer.is_valid(raise_exception=True)
                    instance = serializer.update(serializer.instance,
                                                 serializer.validated_data)
                except IntegrityError as e:
                    raise SuspiciousOperation(
                        f"Updating {self.model} falied. {e.detail}")
                except Exception as e:
                    raise SuspiciousOperation(f"Updating {e.detail} falied.")
                return instance

            if parent:
                data[self.key_field_name] = parent.pk
            return update_model(data) if key in data else create_model(data)

        instances = []
        for data in self.received_data:
            if isinstance(data, dict):
                instances.append(update_or_create_instance(data, parent))
            else:
                instances.append(self.instance_of_pk(pk=data))
        return instances

    def convert_nested_object_ids_to_dicts(self) -> list:
        def serialize_model(data) -> dict:
            instance = data if isinstance(data, models.Model) \
                else self.instance_of_pk(pk=data)
            if instance:
                return self.serializer_class(instance).data
            return None

        resulted_dicts = []
        for data in self.received_data:
            resulted_dicts.append(serialize_model(data))
        return resulted_dicts

    def remove_missing_nested_objects(self, instance, key='id') -> None:
        def delete_objects():
            objects = getattr(instance, self.field_name)
            if type(objects) is not QuerySet:
                objects = self.model.objects
            objects = objects.exclude(pk__in=received_pks).filter(
                **{self.key_field_name: instance})
            objects.delete()

        def remove_objects_link() -> None:
            m2m_existing_pk = getattr(instance, self.m2m_field).values_list(
                key, flat=True).all()
            pks_to_remove = [x for x in m2m_existing_pk
                             if x not in received_pks]
            for pk in pks_to_remove:
                # getattr(instance, self.m2m_field).filter(pk=pk).delete()
                getattr(instance, self.m2m_field).remove(pk)

        received_pks = [x[key] for x in self.received_data if x and key in x]
        if self.m2m_field:
            remove_objects_link()
        elif self.is_parent_dependent:
            delete_objects()

    def instance_of_pk(self, pk) -> models.Model:
        if pk:
            try:
                return self.model.objects.get(pk=pk)
            except self.model.DoesNotExist:
                pass
        return None


class NestedSerializer(serializers.ModelSerializer):
    class Meta:
        nested_objects: list
        computed: list
        abstract: True

    def create(self, data) -> models.Model:
        data = self._put_not_dependent_instances_from_nested_objects(data)
        instance = super().create(data)
        data = self._update_or_create_dependent_objs_from_no(
            instance, data)
        return instance

    def update(self, instance, data) -> models.Model:
        def remove_missing_nested_objects(instance) -> None:
            for no in self.Meta.nested_objects:
                if no.received_data != None and (
                        no.is_parent_dependent or no.m2m_field):
                    no.remove_missing_nested_objects(instance)

        remove_missing_nested_objects(instance)
        data = self._put_not_dependent_instances_from_nested_objects(data)
        instance = super().update(instance, data)
        data = self._update_or_create_dependent_objs_from_no(instance, data)
        return instance

    def to_internal_value(self, data) -> OrderedDict:
        def take_out_computed_from_data(data) -> dict:
            for key in self.Meta.computed:
                if key in data:
                    data.pop(key)
            return data

        def take_out_nested_objects(data) -> dict:
            for no in self.Meta.nested_objects:
                if no.field_name in data:
                    no_data = data.pop(no.field_name)
                    no.received_data = no_data if no.many else [no_data]
            return data

        data = take_out_computed_from_data(data)
        data = take_out_nested_objects(data)
        return super().to_internal_value(data)

    def to_representation(self, data) -> OrderedDict:
        def convert_nested_object_ids_to_dicts(data) -> dict:
            for no in self.Meta.nested_objects:
                no_data = data[no.field_name]
                if no_data != None:
                    no.received_data = no_data if no.many else [no_data]
                    dicts = no.convert_nested_object_ids_to_dicts()
                    data[no.field_name] = dicts if no.many else dicts[0]
            return data

        def remove_parent_form_nested_objects(data) -> dict:
            def remove_parent(field) -> dict:
                if type(field) is ReturnDict and no.key_field_name in field:
                    field.pop(no.key_field_name)
                return field

            for no in self.Meta.nested_objects:
                if no.key_field_name:
                    if type(data[no.field_name]) is list:
                        for field in data[no.field_name]:
                            remove_parent(field)
                    else:
                        remove_parent(data[no.field_name])
            return data

        data = super().to_representation(data)
        data = convert_nested_object_ids_to_dicts(data)
        data = remove_parent_form_nested_objects(data)
        return data

    def _put_not_dependent_instances_from_nested_objects(self, data) -> dict:
        def put_not_dependent_instance(no):
            objects_list = no.update_or_create_instances()
            data[no.field_name] = objects_list if no.many else objects_list[0]

        for no in self.Meta.nested_objects:
            if no.received_data and not no.is_parent_dependent:
                put_not_dependent_instance(no)
        return data

    def _update_or_create_dependent_objs_from_no(self, instance, data) -> dict:
        def update_or_create_dependent_instances(no):
            objects_list = no.update_or_create_instances(parent=instance)
            # data[no.field_name] = objects_list if no.many else objects_list[0]
            if no.is_o2o:
                setattr(instance, no.field_name, objects_list[0])
                instance.save()

        for no in self.Meta.nested_objects:
            if no.received_data and no.is_parent_dependent:
                update_or_create_dependent_instances(no)
        return data
