# from ga_ows.views import wms, wfs
from django.conf import settings as s
from django.contrib.gis.geos import Polygon
import os
import sh
from ga_resources import models as m
import requests
from osgeo import osr, ogr
from . import Driver
import time

VECTOR = False
RASTER = True

DATA_TYPE = VECTOR

class ShapefileDriver(Driver):
    DATA_TYPE = VECTOR

    def __init__(self, data_resource):
        self.resource = data_resource

    def ready_data_resource(self, **kwargs):
        """Other keyword args get passed in as a matter of course, like BBOX, time, and elevation, but this basic driver
        ignores them"""

        cache_path = os.path.join(s.MEDIA_ROOT, ".cache", "resources", *os.path.split(self.resource.slug))

        if not os.path.exists(cache_path):
            os.makedirs(cache_path)

        if self.resource.resource_file:
            _, ext = os.path.splitext(self.resource.resource_file.name)
        elif self.resource.resource_url:
            _, ext = os.path.splitext(self.resource.resource_url)
        else:
            _, ext = os.path.splitext(self.resource.resource_irods_file)

        cached_basename = os.path.join(cache_path, os.path.split(self.resource.slug)[-1])
        cached_filename = cached_basename + ext

        ready = False
        if self.resource.perform_caching and os.path.exists(cached_filename) and ('fresh' not in kwargs or kwargs['fresh'] is False):
            mtime = os.stat(cache_path).st_mtime
            now = time.time()
            ready = now - mtime < self.resource.cache_ttl

        if not ready:
            if self.resource.resource_file:
                if os.path.exists(cached_filename):
                    os.unlink(cached_filename)
                os.symlink(os.path.join(s.MEDIA_ROOT, self.resource.resource_file.name), cached_filename)
            elif self.resource.resource_url:
                result = requests.get(self.resource.resource_url)
                if result.ok:
                    with open(cached_filename, 'wb') as resource_file:
                        resource_file.write(result.content)

            sh.rm('-f', sh.glob(os.path.join(cache_path, '*.shp')))
            sh.rm('-f', sh.glob(os.path.join(cache_path, '*.shx')))
            sh.rm('-f', sh.glob(os.path.join(cache_path, '*.dbf')))
            sh.rm('-f', sh.glob(os.path.join(cache_path, '*.prj')))
            sh.unzip("-o", cached_filename, '-d', cache_path)
            sh.mv(sh.glob(os.path.join(cache_path, '*.shp')), cached_basename + '.shp')
            sh.mv(sh.glob(os.path.join(cache_path, '*.shx')), cached_basename + '.shx')
            sh.mv(sh.glob(os.path.join(cache_path, '*.dbf')), cached_basename + '.dbf')

            try:
                sh.mv(sh.glob(os.path.join(cache_path, '*.prj')), cached_basename + '.prj')
            except:
                with open(cached_basename + '.prj', 'w') as f:
                    srs = osr.SpatialReference()
                    srs.ImportFromEPSG(4326)
                    f.write(srs.ExportToWkt())

            ds = ogr.Open(cached_basename + '.shp')
            lyr = ds.GetLayerByIndex(0)
            xmin, xmax, ymin, ymax = lyr.GetExtent()
            crs = lyr.GetSpatialRef()
            self.resource.spatial_metadata.native_srs = crs.ExportToProj4()
            e4326 = osr.SpatialReference()
            e4326.ImportFromEPSG(4326)
            crx = osr.CoordinateTransformation(crs, e4326)
            x04326, y04326, _ = crx.TransformPoint(xmin, ymin)
            x14326, y14326, _ = crx.TransformPoint(xmax, ymax)
            self.resource.spatial_metadata.bounding_box = Polygon.from_bbox((x04326, y04326, x14326, y14326))
            self.resource.spatial_metadata.native_bounding_box = Polygon.from_bbox((xmin, ymin, xmax, ymax))
            self.resource.spatial_metadata.save()
            self.resource.save()

        return cache_path, (self.resource.slug, self.resource.spatial_metadata.native_srs, {'type': 'shape', "file": cached_basename + '.shp'})

    def compute_fields(self, **kwargs):
        """Other keyword args get passed in as a matter of course, like BBOX, time, and elevation, but this basic driver
        ignores them"""

        cache_path = os.path.join(s.MEDIA_ROOT, ".cache", "resources", *os.path.split(self.resource.slug))

        if not os.path.exists(cache_path):
            os.makedirs(cache_path)

        if self.resource.resource_file:
            _, ext = os.path.splitext(self.resource.resource_file.name)
        elif self.resource.resource_url:
            _, ext = os.path.splitext(self.resource.resource_url)
        else:
            _, ext = os.path.splitext(self.resource.resource_irods_file)

        cached_basename = os.path.join(cache_path, os.path.split(self.resource.slug)[-1])
        cached_filename = cached_basename + ext

        if self.resource.resource_file:
            if os.path.exists(cached_filename):
                os.unlink(cached_filename)
            os.symlink(os.path.join(s.MEDIA_ROOT, self.resource.resource_file.name), cached_filename)
        elif self.resource.resource_url:
            result = requests.get(self.resource.resource_url)
            if result.ok:
                with open(cached_filename, 'wb') as resource_file:
                    resource_file.write(result.content)
            else:
                result.raise_for_status()

        sh.rm('-f', sh.glob(os.path.join(cache_path, '*.shp')))
        sh.rm('-f', sh.glob(os.path.join(cache_path, '*.shx')))
        sh.rm('-f', sh.glob(os.path.join(cache_path, '*.dbf')))
        sh.rm('-f', sh.glob(os.path.join(cache_path, '*.prj')))
        sh.unzip("-o", cached_filename, '-d', cache_path)
        sh.mv(sh.glob(os.path.join(cache_path, '*.shp')), cached_basename + '.shp')
        sh.mv(sh.glob(os.path.join(cache_path, '*.shx')), cached_basename + '.shx')
        sh.mv(sh.glob(os.path.join(cache_path, '*.dbf')), cached_basename + '.dbf')

        try:
            sh.mv(sh.glob(os.path.join(cache_path, '*.prj')), cached_basename + '.prj')
        except:
            with open(cached_basename + '.prj', 'w') as f:
                srs = osr.SpatialReference()
                srs.ImportFromEPSG(4326)
                f.write(srs.ExportToWkt())

        ds = ogr.Open(cached_basename + '.shp')
        lyr = ds.GetLayerByIndex(0)
        xmin, xmax, ymin, ymax = lyr.GetExtent()
        crs = lyr.GetSpatialRef()
        self.resource.spatial_metadata.native_srs = crs.ExportToProj4()
        e4326 = osr.SpatialReference()
        e4326.ImportFromEPSG(4326)
        crx = osr.CoordinateTransformation(crs, e4326)
        x04326, y04326, _ = crx.TransformPoint(xmin, ymin)
        x14326, y14326, _ = crx.TransformPoint(xmax, ymax)
        self.resource.spatial_metadata.bounding_box = Polygon.from_bbox((x04326, y04326, x14326, y14326))
        self.resource.spatial_metadata.native_bounding_box = Polygon.from_bbox((xmin, ymin, xmax, ymax))
        self.resource.spatial_metadata.three_d = False
        self.resource.spatial_metadata.save()
        self.resource.save()

    def get_data_fields(self, **kwargs):
        _, (_, _, result) = self.ready_data_resource(**kwargs)
        ds = ogr.Open(result['file'])
        lyr = ds.GetLayerByIndex(0)
        return [(field.name, field.GetTypeName(), field.width) for field in lyr.schema]

    def get_data_for_point(self, wherex, wherey, srs, fuzziness=0, **kwargs):
        _, (_, nativesrs, result) = self.ready_data_resource(**kwargs)
        ds = ogr.Open(result['file'])
        lyr = ds.GetLayerByIndex(0)

        s_srs = osr.SpatialReference()
        t_srs = osr.SpatialReference()

        if srs.lower().startswith('epsg'):
            s_srs.ImportFromEPSG(int(srs.split(':')[-1]))
        else:
            s_srs.ImportFromProj4(srs)

        t_srs.ImportFromProj4(nativesrs)
        crx = osr.CoordinateTransformation(s_srs, t_srs)
        x1, y1, _ = crx.TransformPoint(wherex, wherey)

        if fuzziness==0:
            lyr.SetSpatialFilter(ogr.CreateGeometryFromWkt("POINT({x1} {y1})".format(**locals())))
        else:
            from django.contrib.gis import geos
            wkt = geos.Point(wherex,wherey).buffer(fuzziness).wkt
            lyr.SetSpatialFilter(ogr.CreateGeometryFromWkt(wkt))
        return [f.items() for f in lyr]


driver = ShapefileDriver