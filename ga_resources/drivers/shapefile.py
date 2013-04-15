# from ga_ows.views import wms, wfs
from django.conf import settings as s
from django.contrib.gis.geos import Polygon
import os
import sh
from ga_resources import models as m
import mapnik
import time
import requests
from collections import OrderedDict
from lxml import etree
from osgeo import osr, ogr
from hashlib import md5

VECTOR = False
RASTER = True

DATA_TYPE = VECTOR

def ready_data_resource(layer, **kwargs):
    """Other keyword args get passed in as a matter of course, like BBOX, time, and elevation, but this basic driver
    ignores them"""

    resource = layer if isinstance(layer, m.DataResource) else m.DataResource.objects.get(slug=layer)
    cache_path = os.path.join(s.MEDIA_ROOT, ".cache", "resources", *os.path.split(resource.slug))

    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    if resource.resource_file:
        _, ext = os.path.splitext(resource.resource_file.name)
    elif resource.resource_url:
        _, ext = os.path.splitext(resource.resource_url)
    else:
        _, ext = os.path.splitext(resource.resource_irods_file)

    cached_basename = os.path.join(cache_path, *os.path.split(resource.slug))
    cached_filename = cached_basename + ext

    #ready = False
    #if resource.perform_caching and os.path.exists(cached_filename) and ('fresh' not in kwargs or kwargs['fresh'] is False):
    #    mtime = os.stat(cache_path).st_mtime
    #    now = time.time()
    #    if now - mtime < resource.cache_ttl:
    #        ready = True
    ready = os.path.exists(cached_filename) # FIXME this must get updated when the cache expires like above, but correctly

    if not ready:
        if resource.resource_file:
            if os.path.exists(cached_filename):
                os.unlink(cached_filename)
            os.symlink(os.path.join(s.MEDIA_ROOT, resource.resource_file.name), cached_filename)
        elif resource.resource_url:
            result = requests.get(resource.resource_url)
            ext = resource.resource_url.split('.')[-1]
            if result.ok:
                with open(cached_filename, 'wb') as resource_file:
                    resource_file.write(result.content)
        elif resource.resource_irods_file:
            pass # TODO figure out how to best support IRODS. I'd rather not copy large resources.

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
        resource.spatial_metadata.native_srs = crs.ExportToProj4()
        e4326 = osr.SpatialReference()
        e4326.ImportFromEPSG(4326)
        crx = osr.CoordinateTransformation(crs, e4326)
        x04326, y04326, _ = crx.TransformPoint(xmin, ymin)
        x14326, y14326, _ = crx.TransformPoint(xmax, ymax)
        resource.spatial_metadata.bounding_box = Polygon.from_bbox((x04326, y04326, x14326, y14326))
        resource.spatial_metadata.native_bounding_box = Polygon.from_bbox((xmin, ymin, xmax, ymax))
        resource.spatial_metadata.save()
        resource.save()

    return cache_path, (resource.slug, resource.spatial_metadata.native_srs, {'type': 'shape', "file": cached_basename + '.shp'})


def compute_fields(resource, **kwargs):
    """Other keyword args get passed in as a matter of course, like BBOX, time, and elevation, but this basic driver
    ignores them"""

    cache_path = os.path.join(s.MEDIA_ROOT, ".cache", "resources", *os.path.split(resource.slug))

    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    if resource.resource_file:
        _, ext = os.path.splitext(resource.resource_file.name)
    elif resource.resource_url:
        _, ext = os.path.splitext(resource.resource_url)
    else:
        _, ext = os.path.splitext(resource.resource_irods_file)

    cached_basename = os.path.join(cache_path, *os.path.split(resource.slug))
    cached_filename = cached_basename + ext

    if resource.resource_file:
        if os.path.exists(cached_filename):
            os.unlink(cached_filename)
        os.symlink(os.path.join(s.MEDIA_ROOT, resource.resource_file.name), cached_filename)
    elif resource.resource_url:
        result = requests.get(resource.resource_url)
        if result.ok:
            with open(cached_filename, 'wb') as resource_file:
                resource_file.write(result.content)
        else:
            result.raise_for_status()
    elif resource.resource_irods_file:
        pass # TODO figure out how to best support IRODS. I'd rather not copy large resources.


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
    resource.spatial_metadata.native_srs = crs.ExportToProj4()
    e4326 = osr.SpatialReference()
    e4326.ImportFromEPSG(4326)
    crx = osr.CoordinateTransformation(crs, e4326)
    x04326, y04326, _ = crx.TransformPoint(xmin, ymin)
    x14326, y14326, _ = crx.TransformPoint(xmax, ymax)
    resource.spatial_metadata.bounding_box = Polygon.from_bbox((x04326, y04326, x14326, y14326))
    resource.spatial_metadata.native_bounding_box = Polygon.from_bbox((xmin, ymin, xmax, ymax))
    resource.spatial_metadata.three_d = False
    resource.spatial_metadata.save()
    resource.save()


