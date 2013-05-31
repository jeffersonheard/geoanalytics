# from ga_ows.views import wms, wfs
from django.conf import settings as s
from django.contrib.gis.geos import Polygon
import os
import sh
import requests
from osgeo import osr, gdal
from . import Driver, VECTOR
import time
from pandas import DataFrame, Panel
from shapely import geometry, wkb
from urllib2 import urlopen
import shutil
from django.template.defaultfilters import slugify
import re
from datetime import datetime
from django.http import Http404

DATA_TYPE = VECTOR

def ogrfield(elt):
    return re.sub('-', '_', slugify(elt).encode('ascii'))[0:10]

class GeotiffDriver(Driver):
    DATA_TYPE = VECTOR

    def ready_data_resource(self, **kwargs):
        """Other keyword args get passed in as a matter of course, like BBOX, time, and elevation, but this basic driver
        ignores them"""

        changed = self.ensure_local_file(freshen='fresh' in kwargs and kwargs['fresh'])
    
        if changed:


            ds = gdal.Open(self.cached_basename + '.tif')
            nx = ds.RasterXSize
            ny = ds.RasterYSize
            x0, dx, _, y0, _, dy = ds.GetGeoTransform()
            xmin, xmax, ymin, ymax = (
                x0,
                x0+dx*nx,
                y0 if dy > 0 else y0 + dy*ny,
                y0 + dy*ny if dy > 0 else y0
            )

            crs = osr.SpatialReference()
            crs.ImportFromWkt(ds.GetProjection())

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

        return self.cache_path, (self.resource.slug, self.resource.spatial_metadata.native_srs, {
            'type': 'gdal',
            "file": self.cached_basename + '.tif'
        })

    def compute_fields(self, **kwargs):
        """Other keyword args get passed in as a matter of course, like BBOX, time, and elevation, but this basic driver
        ignores them"""

        self.ensure_local_file(True)

        ds = gdal.Open(self.cached_basename + '.tif')
        nx = ds.RasterXSize
        ny = ds.RasterYSize
        x0, dx, _, y0, _, dy = ds.GetGeoTransform()
        xmin, xmax, ymin, ymax = (
            x0,
            x0+dx*nx,
            y0 if dy > 0 else y0 + dy*ny,
            y0 + dy*ny if dy > 0 else y0
        )

        crs = osr.SpatialReference()
        crs.ImportFromWkt(ds.GetProjection())

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

    def get_data_fields(self, **kwargs):
        _, (_, _, result) = self.ready_data_resource(**kwargs)
        ds = gdal.Open(result['file'])
        n = ds.RasterCount
        ret = []
        for i in range(1, n+1):
            band = ds.GetRasterBand(i)
            ret.append((
                str(i),
                band.DataType,
                1
            ))

        return ret

    def get_data_for_point(self, wherex, wherey, srs, fuzziness=0, **kwargs):
        _, (_, nativesrs, result) = self.ready_data_resource(**kwargs)
        ds = gdal.Open(result['file'])
        n = ds.RasterCount
        ret = []

        s_srs = osr.SpatialReference()
        t_srs = osr.SpatialReference()

        if srs.lower().startswith('epsg'):
            s_srs.ImportFromEPSG(int(srs.split(':')[-1]))
        else:
            s_srs.ImportFromProj4(srs)

        t_srs.ImportFromProj4(nativesrs)
        crx = osr.CoordinateTransformation(s_srs, t_srs)
        x1, y1, _ = crx.TransformPoint(wherex, wherey)

        nx = ds.RasterXSize
        ny = ds.RasterYSize
        x0, dx, _, y0, _, dy = ds.GetGeoTransform()
        xmin, xmax, ymin, ymax = (
            x0,
            x0+dx*nx,
            y0 if dy > 0 else y0 + dy*ny,
            y0 + dy*ny if dy > 0 else y0
        )

        if x1 < xmin or x1 > xmax or y1 < ymin or y1 > ymax:
            return None
        else:
            xoff = int((x1-xmin) / (xmax-xmin) * nx)
            yoff = int((y1-ymin) / (ymax-ymin) * ny)

            return tuple(ds.ReadAsArray(xoff,yoff,1,1).reshape(ds.RasterCount))


    def as_dataframe(self):
        """
        Creates a dataframe object for a shapefile's main layer using layer_as_dataframe. This object is cached on disk for
        layer use, but the cached copy will only be picked up if the shapefile's mtime is older than the dataframe's mtime.

        :param shp: The shapefile
        :return:
        """

        dfx_path = self.get_filename('dfx')
        tiff_path = self.get_filename('tif')
        if hasattr(self, '_df'):
            return self._df

        elif os.path.exists(dfx_path) and os.stat(dfx_path).st_mtime >= os.stat(tiff_path).st_mtime:
            self._df = Panel.load(dfx_path)
            return self._df
        else:
            ds = gdal.Open(tiff_path)
            try:
                df= Panel(ds.ReadAsArray())
                df.save(dfx_path)
                self._df = df
                return self._df
            except:
                df = DataFrame(ds.ReadAsArray())
                df.save(dfx_path)
                self._df = df
                return self._df

    @classmethod
    def from_dataframe(cls, df, filename, srs, x0, dx, y0, dy, xt=0, yt=0, **metadata):
        """Write an dataframe object out as a geotiff. Note that no interpolation will be done.  Everything must be
        ready as is to be made into an image, including rows, columns, and the final data type.


        """

        dtypes = {
            'uint8' : gdal.GDT_Byte,
            'int64' : gdal.GDT_Int16,
            'float64' : gdal.GDT_Float64,
            'object' : gdal.GDT_Unknown,
            'datetime64[ns]' : gdal.GDT_UInt32
        }

        drv = gdal.GetDriverByName('GTiff')

        if os.path.exists(filename):
            os.unlink(filename)

        cols = df.shape[2]
        rows = df.shape[1]
        bands = df.shape[0] if len(df.shape) == 3 else 1
        dtype = df[0]
        if hasattr(dtype, 'dtype'): # takes care of panel vs. frame
            dtype = dtypes[ dtype.dtype.name ]
        else:
            dtype = dtypes[ dtype[0].dtype.name ]

        ds = drv.Create(filename, cols, rows, bands, dtype)
        ds.SetGeoTransform((x0, dx, xt, y0, yt, dy))
        ds.SetProjection(srs.ExportToWkt())
        for k, v in metadata.items():
            ds.SetMetadata(k, v)

        if isinstance(df, Panel):
            for band in range(1, bands+1):
                b = ds.GetRasterBand(band)
                b.WriteArray(df[band-1].values)
        else:
            b = ds.GetRasterBand(1)
            b.WriteArray(df.values)

        del ds

driver = GeotiffDriver