from app import settings
from django.db import models

class ModelTracker(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        default=None, 
        null=True, 
        on_delete=models.CASCADE, 
        help_text='owner',
        related_name="%(app_label)s_%(class)s_created_by")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        default=None, 
        null=True, 
        on_delete=models.CASCADE, 
        help_text='owner',
        related_name="%(app_label)s_%(class)s_updated_by")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
