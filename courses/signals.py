from django.db.models.signals import pre_delete
from django.dispatch import receiver
import os
from .models import ModulesMediaFile

@receiver(pre_delete, sender=ModulesMediaFile)
def module_media_file_pre_delete(sender, instance, **kwargs):
    if instance.uploaded_file:
        file_path = instance.uploaded_file.path
        if os.path.exists(file_path):
            os.remove(file_path)