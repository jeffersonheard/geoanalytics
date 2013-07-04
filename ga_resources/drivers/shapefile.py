# from ga_ows.views import wms, wfs
from django.conf import settings as s
from django.contrib.gis.geos import Polygon, GEOSGeometry
import os
from osgeo.ogr import Geometry
import sh
from osgeo import osr, ogr
from . import Driver, VECTOR
from pandas import DataFrame
from shapely import geometry, wkb
import shutil
from django.template.defaultfilters import slugify
import re
import json

DATA_TYPE = VECTOR

def ogrfield(elt):
    return re.sub('-', '_', slugify(elt).encode('ascii'))[0:10]

def identity(x):
    return '"' + x + '"' if isinstance(x, basestring) else str(x)


geom_table = {
    'Point' : ogr.wkbPoint,
    'Polygon' : ogr.wkbPolygon,
    'LineString' : ogr.wkbLineString,
    'MultiLineString' : ogr.wkbMultiLineString,
    'MultiPolygon' : ogr.wkbMultiPolygon,
    'MultiPoint' : ogr.wkbMultiPoint
}

def transform(geom, crx):
    if crx:
        geom.Transform(crx)
    return geom


class ShapefileDriver(Driver):
    DATA_TYPE = VECTOR

    def ready_data_resource(self, **kwargs):
        """Other keyword args get passed in as a matter of course, like BBOX, time, and elevation, but this basic driver
        ignores them"""

        changed = self.ensure_local_file(freshen='fresh' in kwargs and kwargs['fresh'])

        if changed:
            self.compute_fields(**kwargs)

        return self.cache_path, (self.resource.slug, self.resource.spatial_metadata.native_srs, {'type': 'shape', "file": self.cached_basename + '.shp'})

    def compute_fields(self, **kwargs):
        """Other keyword args get passed in as a matter of course, like BBOX, time, and elevation, but this basic driver
        ignores them"""

        super(ShapefileDriver, self).compute_fields(**kwargs)

        sh.rm('-f', sh.glob(os.path.join(self.cache_path, '*.shp')))
        sh.rm('-f', sh.glob(os.path.join(self.cache_path, '*.shx')))
        sh.rm('-f', sh.glob(os.path.join(self.cache_path, '*.dbf')))
        sh.rm('-f', sh.glob(os.path.join(self.cache_path, '*.prj')))
        sh.unzip("-o", self.cached_basename + self.src_ext, '-d', self.cache_path)
        
        if not os.path.exists(self.cached_basename + ".shp"):
           sh.mv(sh.glob(os.path.join(self.cache_path, '*.shp')), self.cached_basename + '.shp')
           sh.mv(sh.glob(os.path.join(self.cache_path, '*.shx')), self.cached_basename + '.shx')
           sh.mv(sh.glob(os.path.join(self.cache_path, '*.dbf')), self.cached_basename + '.dbf')

        try:
            sh.mv(sh.glob(os.path.join(self.cache_path, '*.prj')), self.cached_basename + '.prj')
        except:
            with open(self.cached_basename + '.prj', 'w') as f:
                srs = osr.SpatialReference()
                srs.ImportFromEPSG(4326)
                f.write(srs.ExportToWkt())

        ds = ogr.Open(self.cached_basename + '.shp')
        lyr = ds.GetLayerByIndex(0) if 'sublayer' not in kwargs else ds.GetLayerByName(kwargs['sublayer'])
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
        lyr = ds.GetLayerByIndex(0) if 'sublayer' not in kwargs else ds.GetLayerByName(kwargs['sublayer'])
        return [(field.name, field.GetTypeName(), field.width) for field in lyr.schema]

    def get_data_for_point(self, wherex, wherey, srs, fuzziness=0, **kwargs):
        _, (_, nativesrs, result) = self.ready_data_resource(**kwargs)
        ds = ogr.Open(result['file'])
        lyr = ds.GetLayerByIndex(0) if 'sublayer' not in kwargs else ds.GetLayerByName(kwargs['sublayer'])

        s_srs = osr.SpatialReference()
        t_srs = osr.SpatialReference()

        if srs.lower().startswith('epsg'):
            s_srs.ImportFromEPSG(int(srs.split(':')[-1]))
        else:
            s_srs.ImportFromProj4(srs.encode('ascii'))

        t_srs.ImportFromProj4(nativesrs.encode('ascii'))
        crx = osr.CoordinateTransformation(s_srs, t_srs)
        x1, y1, _ = crx.TransformPoint(wherex, wherey)

        if fuzziness==0:
            lyr.SetSpatialFilter(ogr.CreateGeometryFromWkt("POINT({x1} {y1})".format(**locals())))
        else:
            from django.contrib.gis import geos
            wkt = geos.Point(wherex,wherey).buffer(fuzziness).wkt
            lyr.SetSpatialFilter(ogr.CreateGeometryFromWkt(wkt))
        return [f.items() for f in lyr]

    def attrquery(self, key, value):
        key, op = key.split('__')
        op = {
            'gt' : ">",
            'gte' : ">=",
            'lt' : "<",
            'lte' : '<=',
            'startswith' : 'LIKE',
            'endswith' : 'LIKE',
            'istartswith' : 'ILIKE',
            'iendswith' : 'ILIKE',
            'icontains' : "ILIKE",
            'contains' : "LIKE",
            'in' : 'IN',
            'ne' : "<>"
        }[op]

        value = {
            'gt': identity,
            'gte': identity,
            'lt': identity,
            'lte': identity,
            'startswith': lambda x : '%' + x,
            'endswith': lambda x : x + '%',
            'istartswith': lambda x : '%' + x,
            'iendswith': lambda x : x + '%',
            'icontains': lambda x : '%' + x + '%',
            'contains': lambda x: '%' + x + '%',
            'in': lambda x: x if isinstance(x, basestring) else '(' + ','.join(identity(a) for a in x) + ')',
            'ne': identity
        }[op](value)

        return ' '.join([key, op, value])

    def as_dataframe(self, **kwargs):
        """
        Creates a dataframe object for a shapefile's main layer using layer_as_dataframe. This object is cached on disk for
        layer use, but the cached copy will only be picked up if the shapefile's mtime is older than the dataframe's mtime.

        :param shp: The shapefile
        :return:
        """

        dfx_path = self.get_filename('dfx')
        shp_path = self.get_filename('shp')

        if len(kwargs) != 0:
            ds = ogr.Open(shp_path)
            lyr = ds.GetLayerByIndex(0)
            crx=xrc=None

            if 'bbox' in kwargs:
                minx,miny,maxx,maxy = kwargs['bbox']

                if 'srs' in kwargs:
                    if isinstance(kwargs['srs'], basestring):
                        s_srs = osr.SpatialReference()
                        if kwargs['srs'].lower().startswith('epsg:'):
                            s_srs.ImportFromEPSG(int(kwargs['srs'].split(':')[1]))
                        else:
                            s_srs.ImportFromProj4(kwargs['srs'])
                    else:
                        s_srs = kwargs['srs']

                    t_srs = self.resource.srs

                    if s_srs.ExportToProj4() != t_srs.ExportToProj4():
                        crx = osr.CoordinateTransformation(s_srs, t_srs)
                        minx, miny, _ = crx.TransformPoint(minx, miny)
                        maxx, maxy, _ = crx.TransformPoint(maxx, maxy)
                        xrc = osr.CoordinateTransformation(t_srs, s_srs)

                lyr.SetSpatialFilterRect(minx, miny, maxx, maxy)
            elif 'boundary' in kwargs:
                boundary = ogr.Geometry(geom_table[kwargs['boundary_type']], kwargs["boundary"])
                lyr.SetSpatialFilter(boundary)


            if 'query' in kwargs:
                if isinstance(kwargs['query'], basestring):
                    query = json.loads(kwargs['query'])
                else:
                    query = kwargs['query']

                for key, value in query.items():
                    attrq= self.attrquery(key, value) if '__' in key else key, '='
                    lyr.SetAttributeFilter(attrq)

            start = kwargs['start'] if 'start' in kwargs else 0
            count = kwargs['count'] if 'count' in kwargs else len(lyr) - start


            records = []
            for i in range(start):
                lyr.next()

            for i in range(count):
                f = lyr.next()
                if f.geometry():
                    records.append(dict(fid=i, geometry=wkb.loads(transform(f.geometry(), xrc).ExportToWkb()), **f.items()))

            df = DataFrame.from_records(
                data=records,
                index='fid'
            )

            if 'sort_by' in kwargs:
                df = df.sort_index(by=kwargs['sort_by'])

            return df
        elif hasattr(self, '_df'):
            return self._df

        elif os.path.exists(dfx_path) and os.stat(dfx_path).st_mtime >= os.stat(shp_path).st_mtime:
            self._df = DataFrame.load(dfx_path)
            return self._df
        else:
            ds = ogr.Open(shp_path)
            lyr = ds.GetLayerByIndex(0)
            df= DataFrame.from_records(
                data=[dict(fid=f.GetFID(), geometry=wkb.loads(f.geometry().ExportToWkb()), **f.items()) for f in lyr if f.geometry()],
                index='fid'
            )
            df.save(dfx_path)
            self._df = df
            return self._df

    @classmethod
    def from_dataframe(cls, df, shp, srs):
        """Write an dataframe object out as a shapefile"""

        dtypes = {
            'int64' : ogr.OFTInteger,
            'float64' : ogr.OFTReal,
            'object' : ogr.OFTString,
            'datetime64[ns]' : ogr.OFTDateTime
        }
        geomTypes = {
            'GeometryCollection' : ogr.wkbGeometryCollection,
            'LinearRing' : ogr.wkbLinearRing,
            'LineString' : ogr.wkbLineString,
            'MultiLineString' : ogr.wkbMultiLineString,
            'MultiPoint' : ogr.wkbMultiPoint,
            'MultiPolygon' : ogr.wkbMultiPolygon,
            'Point' : ogr.wkbPoint,
            'Polygon' : ogr.wkbPolygon
        }

        drv = ogr.GetDriverByName('ESRI Shapefile')

        if os.path.exists(shp):
            shutil.rmtree(shp)

        os.mkdir(shp)

        ds = drv.CreateDataSource(shp)
        keys = df.keys()
        fieldDefns = [ogr.FieldDefn(ogrfield(name), dtypes[df[name].dtype.name]) for name in keys if name != 'geometry']

        geomType = geomTypes[(f for f in df['geometry']).next().type]
        l = ds.CreateLayer(
            name=os.path.split(shp)[-1],
            srs=srs,
            geom_type=geomType
        )
        for f in fieldDefns:
            l.CreateField(f)

        for i, record in df.iterrows():
            feature = ogr.Feature(l.GetLayerDefn())

            for field, value in ((k, v) for k, v in record.to_dict().items() if k != 'geometry'):
                if isinstance(value, basestring):
                    value=value.encode('ascii')
                feature.SetField(ogrfield(field), value)
            feature.SetGeometry(ogr.CreateGeometryFromWkb(record['geometry'].wkb))
            l.CreateFeature(feature)

        ds.SyncToDisk()
        del ds

driver = ShapefileDriver
