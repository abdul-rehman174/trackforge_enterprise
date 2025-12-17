from django.db import models
from django.conf import settings

class AuditableModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # We use settings.AUTH_USER_MODEL for the custom user you made
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    class Meta:
        abstract = True # This tells Django: "Don't make a table for this, just lend the fields to others"