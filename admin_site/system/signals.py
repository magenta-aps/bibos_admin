from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.core.exceptions import ValidationError

from models import Site


@receiver(pre_delete, sender=Site)
def site_pre_delete(sender, instance, **kwargs):
    site = instance
    if site.pcs.count() > 0:
        raise ValidationError("Unable to delete site with computers attached.")
