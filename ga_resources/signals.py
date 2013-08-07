from mezzanine.pages.models import Page
from mezzanine.core.models import RichText, CONTENT_STATUS_DRAFT, CONTENT_STATUS_PUBLISHED
from mezzanine.core.managers import SearchableManager
from django.contrib.gis.db import models
from django.db.models.signals import post_save, pre_delete, pre_save
from django.conf import settings as s
import importlib
from timedelta.fields import TimedeltaField
import sh
import os
from osgeo import osr
import datetime
from django.utils.timezone import utc
from logging import getLogger
from . import models, tasks
from .models import DataResource, Style, SpatialMetadata


def dataresource_pre_save(sender, instance, *args, **kwargs):
    if 'created' in kwargs and kwargs['created']:
        instance.last_refresh = instance.last_refresh or datetime.datetime.utcnow().replace(tzinfo=utc)
        if instance.refresh_every:
            instance.next_refresh = instance.last_refresh + instance.refresh_every


def dataresource_post_save(sender, instance, *args, **kwargs):
    if instance.status == CONTENT_STATUS_PUBLISHED:
        if not instance.spatial_metadata:
            if 'djcelery' in s.INSTALLED_APPS:
                tasks.data_resource_compute_fields.delay(instance.pk)
            else:
                instance.driver_instance.compute_fields()


pre_save.connect(dataresource_pre_save, sender=DataResource, weak=False)
post_save.connect(dataresource_post_save, sender=DataResource, weak=False)


def purge_cache_on_save(sender, instance, created, *args, **kwargs):
    """Signal handler for styles and data resources that purges the cache using a redis set of files associated with the thing"""
    if not created:
        instance.modified()


def purge_cache_on_delete(sender, instance, *args, **kwargs):
    purge_cache_on_save(sender, instance, False, *args, **kwargs)
    s.WMS_CACHE_DB.delete(instance.slug)


post_save.connect(purge_cache_on_save, sender=Style, weak=False)
post_save.connect(purge_cache_on_save, sender=DataResource, weak=False)
pre_delete.connect(purge_cache_on_delete, sender=Style, weak=False)
pre_delete.connect(purge_cache_on_delete, sender=DataResource, weak=False)


_log = getLogger('ga_resources')
