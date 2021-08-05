from django.db import models
from rest_framework_addons.models import ModelTracker
from django.contrib.auth.models import AbstractUser


from django.contrib.auth.models import AbstractUser


class AppUser(AbstractUser):
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_UNKNOWN = 'X'
    USER_KIND_ADMIN = 0
    USER_KIND_USER = 1
    USER_KIND_OPTIONS = ((USER_KIND_ADMIN, 'admin'),
                         (USER_KIND_USER, 'user'))
    USER_GENDER_OPTIONS = ((GENDER_MALE, 'Male'),
                           (GENDER_MALE, 'Female'),
                           (GENDER_UNKNOWN, 'Unknown'))
    email = models.EmailField(unique=True)
    kind = models.IntegerField(
        choices=USER_KIND_OPTIONS,
        default=1,
        help_text='Type of the user. E.g.: admin')
    phone = models.CharField(
        max_length=20, blank=True,
        help_text='User phone: +40722123456')
    avatar = models.CharField(
        max_length=250,
        default=None,
        null=True,
        blank=True,
        help_text='Link of user avatar photo. E.g. https://aome.cool.pic/123')
    gender = models.CharField(
        choices=USER_GENDER_OPTIONS,
        max_length=1,
        default=GENDER_UNKNOWN,
        help_text='Gender. E.g. M/F')

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'


class MenuItem(ModelTracker):
    name = models.CharField(
        max_length=50,
        help_text='Name of the item. E.g.: Meniuri recomandate')
    icon = models.CharField(
        max_length=50,
        help_text='Icon name. E.g.: stars')
    link = models.CharField(
        max_length=250,
        help_text='Link of the menu. E.g.: ./recomanted')

