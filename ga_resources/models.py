from django.core.serializers import json
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
from hashlib import md5
from logging import getLogger

_log = getLogger('ga_resources')


class CatalogPage(Page):
    """Maintains an ordered catalog of data.  These pages are rendered specially but otherwise are not special."""

    class Meta:
        ordering = ['title']

    @property
    def siblings(self):
        if self.parent:
            return set(self.parent.children.all()) - {self}
        else:
            return set()

    @classmethod
    def ensure_page(cls, *titles, **kwargs):
        parent = kwargs.get('parent', None)
        child = kwargs.get('child', None)
        p, created = cls.objects.get_or_create(title=titles[0], parent=parent)

        for title in titles[1:]:
            p, created = cls.objects.get_or_create(title=title, parent=p)

        if child:
            child.parent = p
            child.save()

        return p

class SemanticRelationship(models.Model):
    """A class to assert a relationship triple between two pages"""
    subject = models.ForeignKey(Page, related_name='subject')
    obj = models.ForeignKey(Page, related_name='obj')
    verb = models.CharField(max_length=128, db_index=True, blank=False, null=False)

    objects = SearchableManager()
    search_fields = ('verb',)


class KeyValue(models.Model):
    """Key-value pair metadata"""
    subject = models.ForeignKey(Page)
    key = models.CharField(max_length=255, db_index=True, blank=False, null=False)
    value = models.TextField(blank=True, null=True)

    objects = SearchableManager()
    search_fields = ("key","value")

class Verb(Page, RichText):
    """A class to provide the metadata about a verb, if it is needed"""
    verb = models.CharField(max_length=128, unique=True, null=False, blank=False)

class SpatialMetadata(models.Model):
    """Automatically generated metadata by the Resource driver"""
    native_bounding_box = models.PolygonField(null=True)
    bounding_box = models.PolygonField(null=True, srid=4326, blank=True)
    three_d = models.BooleanField(default=False)
    native_srs = models.TextField(null=True, blank=True)

class DataResource(Page, RichText):
    """Represents a file that has been uploaded to Geoanalytics for representation"""
    UPLOADED = 1
    URL = 2
    CONFIG = 3

    method = models.PositiveSmallIntegerField(default=UPLOADED, choices=(
        (UPLOADED, 'uploaded'),
        (URL, 'url'),
        (CONFIG, 'configured')
    ))
    resource_file = models.FileField(upload_to='ga_resources', null=True, blank=True)
    resource_url = models.URLField(null=True, blank=True)
    resource_config = models.TextField(null=True, blank=True)
    last_change = models.DateTimeField(null=True, blank=True)
    last_refresh = models.DateTimeField(null=True, blank=True) # updates happen only to resources that were not uploaded by the user.
    next_refresh = models.DateTimeField(null=True, blank=True, db_index=True) # will be populated every time the update manager runs
    refresh_every = TimedeltaField(null=True, blank=True)
    md5sum = models.CharField(max_length=64, blank=True, null=True) # the unique md5 sum of the data

    metadata_url = models.URLField(null=True, blank=True)
    metadata_xml = models.TextField(null=True, blank=True)
    spatial_metadata = models.OneToOneField(SpatialMetadata, null=True, blank=True)

    perform_caching = models.BooleanField(default=True)  # if this is true, then data will be cached
    cache_ttl = models.PositiveIntegerField(default=10, blank=True, null=True)  # if we perform caching, then this is how long in seconds
    data_cache = models.FilePathField(null=True, blank=True)
    driver = models.CharField(default='ga_resources.drivers.shapefile', max_length=255, null=False, blank=False)

    class Meta:
        ordering = ['title']

    @property
    def srs(self):
        srs = osr.SpatialReference()
        srs.ImportFromProj4(self.spatial_metadata.native_srs.encode('ascii'))
        return srs

    @property
    def dataframe(self):
        return self.driver_instance.as_dataframe()

    @property
    def driver_instance(self):
        if not hasattr(self, '_driver_instance'):
            self._driver_instance = importlib.import_module(self.driver).driver(self)
        return self._driver_instance

    def modified(self):
        self.last_refresh = datetime.datetime.utcnow().replace(tzinfo=utc)
        if s.WMS_CACHE_DB.exists(self.slug):
            cached_filenames = s.WMS_CACHE_DB.smembers(self.slug)
            for filename in cached_filenames:
                sh.rm('-rf', sh.glob(filename + "*"))
            sh.rm('-rf', self.cache_path)
            s.WMS_CACHE_DB.srem(self.slug, cached_filenames)



    def refresh(self):
        """
        Called by the automatic refresh mechanism

        :return:
        """
        self.modified()
        self.driver_instance.compute_fields()


    @property
    def cache_path(self):
        p = os.path.join(s.MEDIA_ROOT, ".cache", "resources", *os.path.split(self.slug))
        if not os.path.exists(p):
            os.makedirs(p)  # just in case it's not there yet.
        return p

def dataresource_pre_save(sender, instance, *args, **kwargs):
    if 'created' in kwargs and kwargs['created']:
        instance.last_refresh = instance.last_refresh or datetime.datetime.utcnow().replace(tzinfo=utc)
        if instance.refresh_every:
            instance.next_refresh = instance.last_refresh + instance.refresh_every


def dataresource_post_save(sender, instance, *args, **kwargs):
    if instance.status == CONTENT_STATUS_PUBLISHED:
        if not instance.spatial_metadata:
            instance.spatial_metadata = SpatialMetadata.objects.create()
            instance.driver_instance.compute_fields()
            instance.save()

pre_save.connect(dataresource_pre_save, sender=DataResource, weak=False)
post_save.connect(dataresource_post_save, sender=DataResource, weak=False)


class OrderedResource(models.Model):
    resource_group = models.ForeignKey("ResourceGroup")
    data_resource = models.ForeignKey(DataResource)
    ordering = models.IntegerField(default=0)

class ResourceGroup(Page):
    """Represents a group of resources, which is possibly a time series"""
    resources = models.ManyToManyField(DataResource, blank=True, through=OrderedResource)
    is_timeseries = models.BooleanField(default=False)
    min_time = models.DateTimeField(null=True)
    max_time = models.DateTimeField(null=True)

class AncillaryResource(Page):
    """Represents a file that can be joined onto a vector resource"""
    resource_file = models.FileField(upload_to='ga_resources')
    sqlite_cache = models.FilePathField(null=True)
    foreign_key_resource = models.ForeignKey(DataResource)
    foreign_key = models.CharField(max_length=64)
    local_key = models.CharField(max_length=64)


class Style(Page):
    """A stylesheet in Cascadenik format.  We are switching to Carto shortly."""
    legend = models.ImageField(upload_to='ga_resources.styles.legends', width_field='legend_width', height_field='legend_height', null=True, blank=True)
    legend_width = models.IntegerField(null=True, blank=True)
    legend_height = models.IntegerField(null=True, blank=True)
    stylesheet = models.TextField()

    def modified(self):
        print "purging cache for {slug}".format(slug=self.slug)

        if s.WMS_CACHE_DB.exists(self.slug):
            cached_filenames = s.WMS_CACHE_DB.smembers(self.slug)
            for filename in cached_filenames:
                sh.rm('-rf', sh.glob(filename+"*"))
            s.WMS_CACHE_DB.srem(self.slug, cached_filenames)


class RenderedLayer(Page, RichText):
    """All the general stuff for a layer.  Layers inherit ownership and group info from the data resource"""
    data_resource = models.ForeignKey(DataResource)
    default_style = models.ForeignKey(Style, related_name='default_for_layer')
    styles = models.ManyToManyField(Style)
    cache_seconds = models.PositiveIntegerField(default=60)


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
