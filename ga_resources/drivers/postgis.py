# DO NOT USE. THIS IS A PLACEHOLDER

# from ga_ows.views import wms, wfs
from django.conf import settings
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import D
from osgeo import osr, ogr
from ga_resources.drivers import Driver, VECTOR
from pandas import DataFrame
from shapely import geometry, wkb
from datetime import datetime
from th_core.models import Room
import json

DATA_TYPE = VECTOR

class PostGISDriver(Driver):
    DATA_TYPE = VECTOR

    def ready_data_resource(self, **kwargs):
        """Other keyword args get passed in as a matter of course, like BBOX, time, and elevation, but this basic driver
        ignores them"""

        config = json.loads(self.resource.resource_config)
        table = config['table']
        geometry_field = config.get('geometry_field','geometry')
        use_django_connection = 'hostname' not in config
        if use_django_connection:
            database_route = config.get('database_route', 'default')
            hostname = settings.DATABASES[database_route]['HOST']
            user = settings.DATABASES[database_route]['USER']
            dbname = settings.DATABASES[database_route]['DATABASE']
            password = settings.DATABASES[database_route]['PASSWORD']
            port = settings.DATABASES[database_route]['PORT']
        else:
            hostname = config.get('host','localhost')
            user = config.get('user',None)
            dbname = config['database']
            password = config.get('password',None)
            port = config.get('port',None)

        if 'fresh' in kwargs and kwargs['fresh']:
            if use_django_connection:
                pass # TODO execute SQL on an arbitrary cursor to determine the extent of the geometry in the data
            else:
                pass # TODO create a new psycopg2 conncetion and use a cursor to determine the extent of the geometry

            #xmin, ymin, xmax, ymax = Annotation.objects.extent()
            #crs = osr.SpatialReference()
            #crs.ImportFromEPSG(3857)
            #self.resource.spatial_metadata.native_srs = crs.ExportToProj4()
            #e4326 = osr.SpatialReference()
            #e4326.ImportFromEPSG(4326)
            #crx = osr.CoordinateTransformation(crs, e4326)
            #x04326, y04326, _ = crx.TransformPoint(xmin, ymin)
            #x14326, y14326, _ = crx.TransformPoint(xmax, ymax)

            #self.resource.spatial_metadata.native_srs = crs.ExportToProj4()
            #self.resource.spatial_metadata.bounding_box = Polygon.from_bbox((x04326, y04326, x14326, y14326))
            #self.resource.spatial_metadata.native_bounding_box = Polygon.from_bbox((xmin, ymin, xmax, ymax))
            #self.resource.spatial_metadata.save()
            #self.resource.save()

        return self.cache_path, (self.resource.slug, self.resource.spatial_metadata.native_srs, {
            'type': 'postgis',
            'host': hostname,
            'dbname': dbname,
            'user' : user,
            'password': password,
            'port' : port,
            'table': table,
            'estimate_extent': "True",
            'geometry_field' : geometry_field
        })

    def compute_fields(self, **kwargs):
        """Other keyword args get passed in as a matter of course, like BBOX, time, and elevation, but this basic driver
        ignores them"""

    def get_data_fields(self, **kwargs):
        return [] # (field.name, field.GetTypeName(), field.width) for field in lyr.schema]

    def get_data_for_point(self, wherex, wherey, srs, fuzziness=0, **kwargs):
        raise NotImplementedError("TODO")

    def as_dataframe(self):
        """
        Creates a dataframe object for a shapefile's main layer using layer_as_dataframe. This object is cached on disk for
        layer use, but the cached copy will only be picked up if the shapefile's mtime is older than the dataframe's mtime.

        :param shp: The shapefile
        :return:
        """
        raise NotImplementedError("TODO")

    @classmethod
    def from_dataframe(cls, df, shp, srs):
        """Write an dataframe object out as a shapefile"""
        raise NotImplementedError("TODO")

driver = PostGISDriver
