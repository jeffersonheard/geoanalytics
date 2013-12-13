from django.contrib.auth.models import User
from mezzanine.pages.models import Page
from mezzanine.core.models import RichText
from mezzanine.core.managers import SearchableManager
from django.contrib.gis.db import models
from django.conf import settings as s
import importlib
from timedelta.fields import TimedeltaField
import sh
import os
from osgeo import osr
import datetime
from django.utils.timezone import utc
from logging import getLogger
import json

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

    

class DataResource(Page, RichText):
    """Represents a file that has been uploaded to Geoanalytics for representation"""
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
    native_bounding_box = models.PolygonField(null=True)
    bounding_box = models.PolygonField(null=True, srid=4326, blank=True)
    three_d = models.BooleanField(default=False)
    native_srs = models.TextField(null=True, blank=True)
    public = models.BooleanField(default=True)
    owner = models.ForeignKey(User, null=True)
    edit_users = models.CommaSeparatedIntegerField(max_length=2048, default='', blank=True)
    view_users = models.CommaSeparatedIntegerField(max_length=2048, default='', blank=True)
    edit_groups = models.CommaSeparatedIntegerField(max_length=2048, default='', blank=True)
    view_groups = models.CommaSeparatedIntegerField(max_length=2048, default='', blank=True )
    
    driver = models.CharField(
        default='ga_resources.drivers.spatialite',
        max_length=255,
        null=False,
        blank=False,
        choices=getattr(s, 'INSTALLED_DATARESOURCE_DRIVERS', (
            ('ga_resources.drivers.spatialite', 'Spatialite (universal)'),
            ('ga_resources.drivers.shapefile', 'Shapefile'),
            ('ga_resources.drivers.geotiff', 'GeoTIFF'),
            ('ga_resources.drivers.postgis', 'PostGIS'),
            ('ga_resources.drivers.kmz', 'Google Earth KMZ'),
            ('ga_resources.drivers.ogr', 'OGR DataSource'),
        )))
    big = models.BooleanField(default=False, help_text='Set this to be true if the dataset is more than 100MB') # causes certain drivers to optimize for datasets larger than memory

    class Meta:
        ordering = ['title']

    @property
    def srs(self):
        srs = osr.SpatialReference()
        srs.ImportFromProj4(self.native_srs.encode('ascii'))
        return srs

    @property
    def dataframe(self):
        return self.driver_instance.as_dataframe()

    @property
    def driver_instance(self):
        """deprecated"""
        if not hasattr(self, '_driver_instance'):
            self._driver_instance = importlib.import_module(self.driver).driver(self)
        return self._driver_instance

    @property
    def resource(self):
        return self.driver_instance

    def modified(self):
        self.last_refresh = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.driver_instance.clear_cache()
        
    @property
    def cache_path(self):
        p = os.path.join(s.MEDIA_ROOT, ".cache", "resources", *os.path.split(self.slug))
        if not os.path.exists(p):
            os.makedirs(p)  # just in case it's not there yet.
        return p

    @property
    def driver_config(self):
        return json.loads(self.resource_config) if self.resource_config else {}


    def add_edit_user(self, user):
        users = { int(k) for k in self.edit_users.split(',') }        
        users.add(user.pk)
        self.edit_users = ','.join(str(u) for u in users)


    def add_view_user(self, user):
        users = { int(k) for k in self.view_users.split(',') }        
        users.add(user.pk)
        self.view_users = ','.join(str(u) for u in users)


    def add_edit_group(self, group):
        groups = { int(k) for k in self.edit_groups.split(',') }        
        groups.add(group.pk)
        self.edit_groups = ','.join(str(u) for u in groups)


    def add_view_group(self, group):
        groups = { int(k) for k in self.view_groups.split(',') }        
        groups.add(group.pk)
        self.view_groups = ','.join(str(u) for u in groups)


    def remove_edit_user(self, user):
        users = {int(k) for k in self.edit_users.split(',')}
        users.remove(user.pk)
        self.edit_users = ','.join(str(u) for u in users)


    def remove_view_user(self, user):
        users = {int(k) for k in self.view_users.split(',')}
        users.remove(user.pk)
        self.view_users = ','.join(str(u) for u in users)


    def remove_edit_group(self, group):
        groups = {int(k) for k in self.edit_groups.split(',')}
        groups.remove(group.pk)
        self.edit_groups = ','.join(str(u) for u in groups)


    def remove_view_group(self, group):
        groups = {int(k) for k in self.view_groups.split(',')}
        groups.remove(group.pk)
        self.view_groups = ','.join(str(u) for u in groups)    


    def can_add(self, request):
        if request.user.is_authenticated():
            if not self.owner:
                return request.user.is_superuser
            elif request.user.pk == self.owner.pk:
                return True
            else:
                users = {int(k) for k in self.edit_users.split(',')}
                groups = {int(k) for k in self.edit_groups.split(',')}

                if len(users) > 0 and request.user.pk in users:
                    return True
                elif len(groups) > 0:
                    return request.user.groups.filter(pk__in=groups).exists()
                else:
                    return False

    def can_delete(self, request):
        if request.user.is_authenticated():
            if not self.owner:
                return request.user.is_superuser
            elif request.user.pk == self.owner.pk:
                return True
            else:
                users = {int(k) for k in self.edit_users.split(',')}
                groups = {int(k) for k in self.edit_groups.split(',')}

                if len(users) > 0 and request.user.pk in users:
                    return True
                elif len(groups) > 0:
                    return request.user.groups.filter(pk__in=groups).exists()
                else:
                    return False
    
    
    def can_change(self, request):
        if request.user.is_authenticated():
            if not self.owner:
                return request.user.is_superuser
            elif request.user.pk == self.owner.pk:
                return True
            else:
                users = {int(k) for k in self.edit_users.split(',')}
                groups = {int(k) for k in self.edit_groups.split(',')}

                if len(users) > 0 and request.user.pk in users:
                    return True
                elif len(groups) > 0:
                    return request.user.groups.filter(pk__in=groups).exists()
                else:
                    return False
    
    
    def can_view(self, request):
        if self.public:
            return True
        if request.user.is_authenticated():
            if not self.owner:
                return request.user.is_superuser
            elif request.user.pk == self.owner.pk:
                return True
            else:
                users = {int(k) for k in self.view_users.split(',')}
                groups = {int(k) for k in self.view_groups.split(',')}

                if len(users) > 0 and request.user.pk in users:
                    return True
                elif len(groups) > 0:
                    return request.user.groups.filter(pk__in=groups).exists()
                else:
                    return False
        
        

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

class RelatedResource(Page, RichText):
    """Represents a file that can be joined onto a vector resource"""
    UPPERCASE = 0
    CAPITALIZE = 1
    LOWERCASE = 2

    resource_file = models.FileField(upload_to='ga_resources')
    foreign_resource = models.ForeignKey(DataResource)
    foreign_key = models.CharField(max_length=64, blank=True, null=True)
    local_key = models.CharField(max_length=64, blank=True, null=True)
    left_index = models.BooleanField(default=False)
    right_index = models.BooleanField(default=False)
    how = models.CharField(max_length=8, default='left', choices=(
        ('left','left'),
        ('right','right'),
        ('outer','outer'),
        ('inner','inner'),
    ))
    driver = models.CharField(max_length=255,default='ga_resources.drivers.related.excel')
    key_transform = models.IntegerField(blank=True, null=True, choices=(
        (CAPITALIZE, "Capitalize"),
        (LOWERCASE, "Lower case"),
        (UPPERCASE, "Upper case")
    ))

    @property
    def driver_instance(self):
        if not hasattr(self, '_driver_instance'):
            self._driver_instance = importlib.import_module(self.driver).driver(self)
        return self._driver_instance

    @property
    def cache_path(self):
        p = os.path.join(s.MEDIA_ROOT, ".cache", "resources", *os.path.split(self.slug))
        if not os.path.exists(p):
            os.makedirs(p)  # just in case it's not there yet.
        return p

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
    default_class = models.CharField(max_length=255, default='default')
    styles = models.ManyToManyField(Style)
    cache_seconds = models.PositiveIntegerField(default=60)


