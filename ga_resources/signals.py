from django.db.models.signals import post_save, pre_delete, pre_save
from django.conf import settings as s
import datetime
from django.utils.timezone import utc
from logging import getLogger
from . import tasks
from .models import DataResource, Style
import os


def dataresource_pre_save(sender, instance, *args, **kwargs):
    if 'created' in kwargs and kwargs['created']:
        instance.last_refresh = instance.last_refresh or datetime.datetime.utcnow().replace(tzinfo=utc)
        if instance.refresh_every:
            instance.next_refresh = instance.last_refresh + instance.refresh_every


def dataresource_post_save(sender, instance, *args, **kwargs):
    if not instance.native_srs:
        if instance.big:
            tasks.data_resource_compute_fields.delay(instance.pk)
        else:
            instance.driver_instance.compute_fields()


pre_save.connect(dataresource_pre_save, sender=DataResource, weak=False)
post_save.connect(dataresource_post_save, sender=DataResource, weak=False)

def purge_cache_on_delete(sender, instance, *args, **kwargs):
    instance.resource.clear_cache()
    if instance.resource_file:
        os.unlink(os.path.join(s.MEDIA_ROOT, instance.resource_file.name))
    s.WMS_CACHE_DB.delete(instance.slug)

pre_delete.connect(purge_cache_on_delete, sender=Style, weak=False)
pre_delete.connect(purge_cache_on_delete, sender=DataResource, weak=False)


_log = getLogger('ga_resources')
