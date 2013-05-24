from mezzanine.pages.models import Page
from mezzanine.core.models import RichText
from django.contrib.gis.db import models
from django.db.models.signals import post_save, pre_delete
from django.conf import settings as s
import importlib
import sh
import os
from osgeo import osr


class SpatialMetadata(models.Model):
    native_bounding_box = models.PolygonField(null=True)
    bounding_box = models.PolygonField(null=True, srid=4326, blank=True)
    three_d = models.BooleanField(default=False)
    native_srs = models.TextField(null=True, blank=True)

class DataResource(Page, RichText):
    """Represents a file that has been uploaded to Geoanalytics for representation"""
    UPLOADED = 1
    URL = 2

    method = models.PositiveSmallIntegerField(default=UPLOADED, choices=(
        (UPLOADED, 'uploaded'),
        (URL, 'url'),
    ))
    resource_file = models.FileField(upload_to='ga_resources', null=True, blank=True)
    resource_url = models.URLField(null=True, blank=True)
    time_represented = models.DateTimeField(null=True, db_index=True, blank=True)
    perform_caching = models.BooleanField(default=True)  # if this is true, then data will be cached
    cache_ttl = models.PositiveIntegerField(default=10, blank=True, null=True)  # if we perform caching, then this is how long in seconds
    data_cache = models.FilePathField(null=True, blank=True)
    driver = models.CharField(default='ga_resources.drivers.shapefile', max_length=255, null=False, blank=False)
    spatial_metadata = models.OneToOneField(SpatialMetadata, null=True, blank=True)

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
        print "purging cache for {slug}".format(slug=self.slug)

        if s.WMS_CACHE_DB.exists(self.slug):
            cached_filenames = s.WMS_CACHE_DB.smembers(self.slug)
            for filename in cached_filenames:
                sh.rm('-rf', sh.glob(filename + "*"))

            sh.rm('-rf', self.cache_path)

            s.WMS_CACHE_DB.srem(self.slug, cached_filenames)

    @property
    def cache_path(self):
        p = os.path.join(s.MEDIA_ROOT, ".cache", "resources", *os.path.split(self.slug))
        if not os.path.exists(p):
            os.makedirs(p)  # just in case it's not there yet.
        return p


def dataresource_post_save(sender, instance, *args, **kwargs):
    if 'created' in kwargs and kwargs['created']:
        instance.spatial_metadata = SpatialMetadata.objects.create()
        instance.driver_instance.compute_fields()

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
    """An XML stylesheet in MML format for WMS or WMTS output

    OR

    A visual raster needs no style, but raw data does.  We do this with a JSON object describing a palette:

    "empty" : optional color to make empty cells
    "empty_value" : if empty is defined, define a value that indicates an empty cell
    "filled" : a series of palette entries representing the palette for filled objects
    "numexpr" : a numeric transform to be applied to get a final scalar.  If the raster has multiple bands, then we can
                use, in series, variables "a", "b", "c" ... "z"
    "bands" : a list of band names (Pandas, NetCDF) or indices (GDAL)

    "exact" : a palette entry for an exact value
    "xx" : an exclusive range, one where neither side is included in the translation
    "oo" : an inclusive range, one where both sides are included in the translation
    "ox" : a left (low) inclusive range
    "xo" : a right (high) inclusive range

    "interpolation" : either "round", "ceiling", "floor", "linear" (default) or "sin" interpolation between colors.

    [0, "rgba(255,0,0,1.0)", ...] : an arbitrarily long list of stop values and their associated colors.

    Example:

    { "empty" : "rgba(0,0,0,0)",
      "empty_value" : -9999.0,
      "bands" : [ names or numbers ]
      "numexpr" : "sqrt(a)"
      "filled" : [
        { "exact" : [0, "rgba(255,255,255,1.0)"] },
        { "interpolation": "sin", "xx" : [0, "rgba(255,0,0,1.0)", 10, "rgba(255,255,0,1.0)", ... ] },
        { "ox" : [10, ..., 20, ... ] },
        { "oo" : [20, ..., 255, ... ] }
      ]
    }
    """
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

class StyleTemplate(Page):
    """A template stylesheet in Python Template format for quickly creating styles from well-known styles. """
    stylesheet = models.TextField()


class StyleTemplateVariable(models.Model):
    """Template variables for style templates"""
    name = models.CharField(max_length=64)
    kind = models.CharField(max_length=24, default='attribute', choices=(
        ('integer', 'int'),
        ('floating point', 'float'),
        ('string', 'string'),
        ('attribute name', 'attribute')
    ))
    default_value = models.CharField(max_length=255, blank=True)


class RenderedLayer(Page, RichText):
    """All the general stuff for a layer.  Layers inherit ownership and group info from the data resource"""
    data_resource = models.ForeignKey(DataResource)
    default_style = models.ForeignKey(Style, related_name='default_for_layer')
    styles = models.ManyToManyField(Style)
    cache_seconds = models.PositiveIntegerField(default=60)

class AnimatedResourceLayer(Page, RichText):
    """A rendered animated resource similar to WMS, but renderable to animated gif of mkv"""
    data_resource = models.ForeignKey(DataResource)
    default_style = models.ForeignKey(Style, related_name='default_for_animation')
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