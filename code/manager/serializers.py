from django.core.exceptions import SuspiciousOperation
from django.db.models import fields
from django.db.utils import IntegrityError
from rest_framework_addons.serializers import NestedObject, NestedSerializer
from rest_framework import serializers
from manager.models import AppUser, MenuItem


class AppUserSerializer(NestedSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = AppUser
        computed = ['name']
        fields = ['id',
                  'username',
                  'email',
                  'password',
                  'last_login',
                  'first_name',
                  'last_name',
                  'phone',
                  'avatar',
                  'gender',
                  'date_joined',
                  'kind'] + computed
        nested_objects = []

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'icon', 'link']
