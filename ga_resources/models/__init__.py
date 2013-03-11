from django.template.defaultfilters import slugify
from django.utils.timezone import now
from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from ga_irods.models import RodsEnvironment

class SlugifiedModel(models.Model):
    """Slugifies name upon save"""
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField()

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.slug = slugify(self.name)

    class Meta:
        abstract = True


class DataResource(models.Model):
    """Represents a file that has been uploaded to Geoanalytics for representation"""
    UPLOADED = 1
    URL = 2
    IRODS = 3

    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField()
    method = models.PositiveSmallIntegerField(default=UPLOADED, choices=(
        (UPLOADED, 'uploaded'),
        (URL, 'url'),
        (IRODS, 'irods')
    ))
    resource_file = models.FileField(upload_to='ga_resources', null=True)
    resource_url = models.URLField(null=True)
    resource_irods_env = models.ForeignKey(RodsEnvironment, null=True)  # if this is not null, we use ga_irods to access
    resource_irods_file = models.FilePathField(null=True)
    owner = models.ForeignKey(User)
    timestamp = models.DateTimeField(default=now, db_index=True)
    time_represented = models.DateTimeField(null=True, db_index=True)
    access_groups = models.ManyToManyField(Group, related_name='data_resource_access_groups', null=True)
    modify_groups = models.ManyToManyField(Group, related_name='data_resource_modify_groups', null=True)
    anonymous_read = models.BooleanField(default=True)  # if this is true, then anyone can read
    perform_caching = models.BooleanField(default=True)  # if this is true, then data will be cached
    cache_ttl = models.PositiveIntegerField(default=10)  # if we perform caching, then this is how long in seconds
    data_cache = models.FilePathField(null=True, blank=True)
    bounding_box = models.PolygonField(null=True, srid=4326)
    kind = models.CharField(max_length=24, default='vector', choices=(()))
    driver = models.CharField(default='ga_resources.drivers.ogr', max_length=255, null=False, blank=False)


class ResourceGroup(models.Model):
    """Represents a group of resources, which is possibly a time series"""
    resources = models.ManyToManyField(DataResource, blank=True)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField()
    is_timeseries = models.BooleanField(default=False)
    min_time = models.DateTimeField(null=True)
    max_time = models.DateTimeField(null=True)


class AncillaryResource(models.Model):
    """Represents a file that can be joined onto a vector resource"""
    resource_file = models.FileField(upload_to='ga_resources')
    sqlite_cache = models.FilePathField(null=True)
    foreign_key_resource = models.ForeignKey(DataResource)
    foreign_key = models.CharField(max_length=64)
    local_key = models.CharField(max_length=64)


class Style(models.Model):
    """An XML stylesheet in Mapnik format for WMS or WMTS output

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
    name = models.CharField(max_length=255, db_index=True)
    legend = models.ImageField(upload_to='ga_resources.styles.legends')
    slug = models.SlugField()
    stylesheet_file = models.FileField(upload_to='ga_resources.styles')


class StyleTemplate(models.Model):
    """A template stylesheet in Python Template format for quickly creating styles from well-known styles. """
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField()
    stylesheet_file = models.FileField(upload_to='ga_resources.style_templates')


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


class LayerGroup(models.Model):
    """A way to group layers into separate virtual services to keep capabilites responses from being too long"""
    name = models.CharField(max_length=255, blank=False, db_index=True)
    slug = models.SlugField()
    abstract = models.TextField()


class Layer(models.Model):
    """All the general stuff for a layer.  Layers inherit ownership and group info from the data resource"""
    layer_group = models.ForeignKey(LayerGroup)
    name = models.CharField(max_length=255, blank=False, unique=True, db_index=True)
    slug = models.SlugField()
    title = models.TextField()
    abstract = models.TextField()
    data_resource = models.ForeignKey(DataResource)

    class Meta:
        abstract = True


class WMSLayer(Layer):
    """A WMS layer"""
    default_style = models.ForeignKey(Style, related_name='default_wms_layer')
    styles = models.ManyToManyField(Style, related_name='wms_layer')


class WMVSLayer(Layer):
    """Similar to WMS but for an animation of a timeseries"""
    default_style = models.ForeignKey(Style, related_name='default_wmvs_layer')
    styles = models.ManyToManyField(Style, related_name='wmvs_layer')


class WMTSLayer(Layer):
    """A tiled map service layer"""
    default_style = models.ForeignKey(Style, related_name='default_wmts_layer')
    styles = models.ManyToManyField(Style, related_name='wmts_layer')


class WFSLayer(Layer):
    """A WFS layer"""


class WCSLayer(Layer):
    """A WCS layer"""


class SOSLayer(Layer):
    """A sensor observation service layer"""
