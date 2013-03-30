from mezzanine.pages.models import Page
from mezzanine.core.models import RichText
from django.contrib.gis.db import models
from ga_irods.models import RodsEnvironment
import importlib

from ga_resources.managers import GeoPageManager


class DataResource(Page, RichText):
    """Represents a file that has been uploaded to Geoanalytics for representation"""
    UPLOADED = 1
    URL = 2
    IRODS = 3

    method = models.PositiveSmallIntegerField(default=UPLOADED, choices=(
        (UPLOADED, 'uploaded'),
        (URL, 'url'),
        (IRODS, 'irods')
    ))
    resource_file = models.FileField(upload_to='ga_resources', null=True)
    resource_url = models.URLField(null=True, blank=True)
    resource_irods_env = models.ForeignKey(RodsEnvironment, null=True, blank=True)  # if this is not null, we use ga_irods to access
    resource_irods_file = models.FilePathField(null=True, blank=True)
    time_represented = models.DateTimeField(null=True, db_index=True, blank=True)
    perform_caching = models.BooleanField(default=True)  # if this is true, then data will be cached
    cache_ttl = models.PositiveIntegerField(default=10, blank=True, null=True)  # if we perform caching, then this is how long in seconds
    data_cache = models.FilePathField(null=True, blank=True)
    bounding_box = models.PolygonField(null=True, srid=4326, blank=True)
    kind = models.CharField(max_length=24, default='vector', choices=(('vector','Vector'),('raster','Raster')))
    driver = models.CharField(default='ga_resources.drivers.ogr', max_length=255, null=False, blank=False)
    native_srs = models.TextField(null=True, blank=True)

    objects = GeoPageManager()

    def save(self, *args, **kwargs):
        driver = importlib.import_module(self.driver)
        driver.compute_fields(self)
        super(DataResource, self).save(*args, **kwargs)




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


class RasterResourceLayer(Page, RichText):
    """A raw raster resource as might be retrieved via WCS"""
    data_resource = models.ForeignKey(DataResource)
    styled_layer = models.ForeignKey(RenderedLayer, null=True, blank=True)


class VectorResourceLayer(Page, RichText):
    """A raw vector resource as might be retrieved via WFS"""
    data_resource = models.ForeignKey(DataResource)
    styled_layer = models.ForeignKey(RenderedLayer, null=True, blank=True)


class AnimatedResourceLayer(Page, RichText):
    """A rendered animated resource similar to WMS, but renderable to animated gif of mkv"""
    data_resource = models.ForeignKey(DataResource)
    default_style = models.ForeignKey(Style, related_name='default_for_animation')
    styles = models.ManyToManyField(Style)
