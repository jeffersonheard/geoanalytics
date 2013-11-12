# from ga_ows.views import wms, wfs
from uuid import uuid4
from django.contrib.gis.geos import Polygon, GEOSGeometry
import os
from osgeo import osr
from . import Driver
from pandas import DataFrame
import sh
from shapely import geometry, wkb
import json
import pandas
from pysqlite2 import dbapi2 as db
import geojson
import shapely

def identity(x):
    return '"' + x + '"' if isinstance(x, basestring) else str(x)


def transform(geom, crx):
    if crx:
        geom.Transform(crx)
    return geom


class SpatialiteDriver(Driver):
    """
    Config Parameters:
        * dbname : string (required if not use_django_dbms)
        * table : the default table to use
        * tables : dict of layer names -> tables, must all be in the same coordinate system for now.  Can also be select queries. paired with the geometry field name.
        * estimate_extent : see mapnik documentation
        * srid : the native srid of the tables
    """
    def __init__(self, data_resource):
        super(SpatialiteDriver, self).__init__(data_resource)
        self._conn = None # lazily open the connection


    def ready_data_resource(self, **kwargs):
        slug, srs = super(SpatialiteDriver, self).ready_data_resource(**kwargs)
        cfg = self.resource.driver_config

        connection = self._connection()
        conn = {
            'type': 'sqlite',
            'file': self.get_filename('sqlite'),
        }

        if 'table' not in cfg:
            table, geometry_field, _, _, srid, _ = connection.execute("select * from geometry_columns").fetchone() # grab the first layer with a geometry
            self._tablename = table
            self._geometry_field = geometry_field
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(srid)
            self._srid = srs.ExportToProj4()
        elif 'sublayer' in kwargs:
            table, geometry_field = cfg['tables']['sublayer']
        else:
            table, geometry_field = cfg['table']

        def addcfg(k):
            if k in cfg:
                conn[k] = cfg[k]

        addcfg('key_field')
        addcfg('encoding')

        self._table_name = conn['table'] = table
        self._geometry_field = conn['geometry_field'] = geometry_field

        return slug, srs, conn

    def _connection(self):
        # create a database connection, or use the
        if self._conn is None:
            conn = db.connect(self.get_filename('sqlite'))
            conn.enable_load_extension(True)
            conn.execute("select load_extension('libspatialite.so')")
            self._conn = conn
        return self._conn

    def compute_fields(self, **kwargs):
        """Other keyword args get passed in as a matter of course, like BBOX, time, and elevation, but this basic driver
        ignores them"""
        
        super(SpatialiteDriver, self).compute_fields(**kwargs)
        cfg = self.resource.driver_config
        connection = self._connection()
        table, geometry_field, _, _, srid, _ = connection.execute("select * from geometry_columns").fetchone() # grab the first layer with a geometry

        xmin = ymin = float('inf')
        ymax = xmax = float('-inf')

        dataframe = self.get_filename('dfx')
        if os.path.exists(dataframe):
            os.unlink(dataframe)

        c = connection.cursor()
        c.execute("select AsText(Envelope(w.{geom_field})) from {table} as w".format(
            geom_field=geometry_field,
            table=table
        ))

        xmin0, ymin0, xmax0, ymax0 = GEOSGeometry(c.fetchone()[0]).extent
        xmin = xmin0 if xmin0 < xmin else xmin
        ymin = ymin0 if ymin0 < ymin else ymin
        xmax = xmax0 if xmax0 < xmax else xmax
        xmax = xmax0 if xmax0 < xmax else xmax

        crs = osr.SpatialReference()
        crs.ImportFromEPSG(srid)
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

    def _table(self, **kwargs):
        if not hasattr(self, '_geometry_field'):
            self.ready_data_resource(**kwargs)

        cfg = self.resource.driver_config
        if 'sublayer' in kwargs:
            table, geometry_field = cfg['tables'][kwargs['sublayer']]
        else:
            table, geometry_field = self._tablename, self._geometry_field

        return table, geometry_field

    def get_data_for_point(self, wherex, wherey, srs, fuzziness=0, **kwargs):
        result, x1, y1 = super(SpatialiteDriver, self).get_data_for_point(wherex, wherey, srs, fuzziness, **kwargs)
        cfg = self.resource.driver_config
        table, geometry_field = self._table(**kwargs)

        if fuzziness == 0:
            geometry = "GeomFromText('POINT({x} {y})', {srid})".format(
                x=x1,
                y=y1,
                srid=cfg['srid']
            )
        else:
            geometry = "ST_Buffer(GeomFromText('POINT({x} {y})', {srid}), {fuzziness})".format(
                x=x1,
                y=y1,
                srid=cfg['srid']
            )

        cursor = self._cursor(**kwargs)
        if table.strip().lower().startswith('select'):
            table = '(' + table + ")"

        cursor.execute("SELECT * FROM {table} as w WHERE ST_Intersects({geometry}, w.{geometry_field})".format(
            geometry=geometry,
            table=table,
            geometry_field=geometry_field
        ))
        rows = [list(r) for r in cursor.fetchall()]
        keys = [c.name for c in cursor.description]

        return [zip(keys, r) for r in rows]

    def attrquery(self, key, value):
        if '__' not in key:
            return key + '=' + value

        key, op = key.split('__')
        op = {
            'gt': ">",
            'gte': ">=",
            'lt': "<",
            'lte': '<=',
            'startswith': 'LIKE',
            'endswith': 'LIKE',
            'istartswith': 'ILIKE',
            'iendswith': 'ILIKE',
            'icontains': "ILIKE",
            'contains': "LIKE",
            'in': 'IN',
            'ne': "<>"
        }[op]

        value = {
            'gt': identity,
            'gte': identity,
            'lt': identity,
            'lte': identity,
            'startswith': lambda x: '%' + x,
            'endswith': lambda x: x + '%',
            'istartswith': lambda x: '%' + x,
            'iendswith': lambda x: x + '%',
            'icontains': lambda x: '%' + x + '%',
            'contains': lambda x: '%' + x + '%',
            'in': lambda x: x if isinstance(x, basestring) else '(' + ','.join(identity(a) for a in x) + ')',
            'ne': identity
        }[op](value)

        return ' '.join([key, op, value])

    def _cursor(self, **kwargs):
        self.ready_data_resource()
        connection = self._connection()
        if 'big' in kwargs or (
                self.resource.big and 'count' not in kwargs): # if we don't have control over the result size of a big resource, use a server side cursor
            cursor = connection.cursor('cx' + uuid4().hex)
        else:
            cursor = connection.cursor()

        return cursor


    def as_dataframe(self, **kwargs):
        """
        Creates a dataframe object for a shapefile's main layer using layer_as_dataframe. This object is cached on disk for
        layer use, but the cached copy will only be picked up if the shapefile's mtime is older than the dataframe's mtime.

        :param shp: The shapefile
        :return:
        """

        dfx_path = self.get_filename('dfx')

        if len(kwargs) != 0:
            cfg = self.resource.driver_config
            lyr = {}
            crx = xrc = None

            if 'bbox' in kwargs:
                minx, miny, maxx, maxy = kwargs['bbox']

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

                lyr['bbox'] = (minx, miny, maxx, maxy)
            elif 'boundary' in kwargs:
                lyr['boundary'] = kwargs['boundary']

            if 'query' in kwargs:
                lyr['query'] = []

                if isinstance(kwargs['query'], basestring):
                    query = json.loads(kwargs['query'])
                else:
                    query = kwargs['query']

                lyr['query'] = ' AND '.join(self.attrquery(key, value) for key, value in query.items())

            start = kwargs['start'] if 'start' in kwargs else 0
            count = start + kwargs['count'] if 'count' in kwargs else -1


            # contsruct query

            cursor = self.connection # _cursor(**kwargs)

            q = "SELECT AsBinary({geometry_column}), * FROM ({table}) AS w WHERE "
            addand = False
            if 'bbox' in lyr:
                q += "ST_Intersects(GeomFromText('BBOX({xmin} {ymin} {xax} {ymax})'), {geometry_column})"
                addand = True

            if 'boundary' in lyr:
                q += "ST_Intersects(GeomFromText('{boundary}', {geometry_column}))"
                addand = True

            if 'query' in lyr:
                if addand:
                    q += ' AND '
                q += lyr['query']

            if count > 0:
                q += ' LIMIT {count}'.format(count=count)

            table, geometry_column = self._table(**kwargs)
            if table.strip().lower().startswith('select'):
                table = '(' + table + ")"

            cursor.execute(q.format(
                boundary=cfg.get('boundary', None),
                geometry_column=geometry_column,
                table=table,
                **lyr.get('bbox', [None, None, None, None])
            ))
            for i in range(start):
                cursor.fetchone()

            names = [c[0] for c in cursor.description]
            throwaway_ix = names[1:].index(geometry_column) + 1
            records = []
            for record in cursor:
                records.append({name: value for i, (name, value) in enumerate(zip(names, record)) if i != throwaway_ix})
                records[-1]['geometry'] = wkb.loads(record['asbinary'])

            df = DataFrame.from_records(
                data=records,
                index='fid'
            )

            if 'sort_by' in kwargs:
                df = df.sort_index(by=kwargs['sort_by'])

            return df

        elif hasattr(self, '_df'):
            return self._df

        elif os.path.exists(dfx_path):
            self._df = pandas.read_pickle(dfx_path)
            return self._df
        else:
            table, geometry_column = self._table(**kwargs)

            query = "SELECT AsBinary({geometry_column}), * FROM {table}".format(table=table,
                                                                                geometry_column=geometry_column)
            cursor = self._cursor(**kwargs)
            cursor.execute("select load_extension('libspatialite.so')")


            cursor.execute(query)
            names = [c[0] for c in cursor.description]

            throwaway_ix = names[1:].index(geometry_column) + 1
            records = []
            for record in cursor:
                records.append({name: value for i, (name, value) in enumerate(zip(names, record)) if i != throwaway_ix})
                records[-1]['geometry'] = wkb.loads(str(records[-1]['AsBinary(GEOMETRY)']))
                del records[-1]['AsBinary(GEOMETRY)']

            df = DataFrame.from_records(data=records)
            df.to_pickle(dfx_path)
            self._df = df
            return self._df

    def add_column(self, name, field_type):
        c = self._cursor()
        c.execute('alter table {table} add column {column_name} {column_type}'.format(
            table=self._tablename,
            column_name=name,
            column_type=field_type
        ))
        c.close()
        self.resource.modified()

    def delete_row(self, key):
        c = self._cursor()
        c.execute('delete from {table} where ogc_fid={key}'.format(
            table=self._tablename,
            key=key
        ))
        c.close()
        self.resource.modified()

    def add_row(self, **values):
        c = self._cursor()
        insert_stmt = 'insert into {table} ({keys}) values ({values})'
        keys = list(values.keys())
        values = [values[key] for key in keys]
        parms = ','.join(['?' for key in keys])
        insert_stmt.format(
            table=self._tablename,
            keys=keys,
            values=parms
        )
        c.execute(insert_stmt, values)
        c.close()
        self.resource.modified()

    def update_row(self, ogc_fid, **values):
        c = self._cursor()
        insert_stmt = 'update {table} set {set_clause} where OGC_FID={ogc_fid}'
        table = self._tablename
        set_clause = ' and '.join(["{key}=:{key}".format(key=key) for key in values.keys()])
        c.execute(insert_stmt.format(**locals()), values)

    def get_row(self, ogc_fid, geometry_format='geojson'):
        c = self._cursor()
        keys = self.schema()
        table = self._tablename
        geometry = self._geometry_field

        select = 'select * from {table} where OGC_FID={ogc_fid}'.format(**locals())
        select2 = 'select AsBinary({geometry}) from {table} where OGC_FID={ogc_fid}'.format(**locals())

        c.execute("select load_extension('libspatialite.so')")
        record = dict(p for p in zip(keys, c.execute(select).fetchone()) if p[0] != geometry)
        geo = c.execute(select2).fetchone()
        # gj = { 'type' : 'feature', 'geometry' : json.loads(geojson.dumps(wkb.loads(str(geo[0])))), 'properties' : record }
        gj = record
        if geometry_format.lower() == 'geojson':
            gj[self._geometry_field] = json.loads(geojson.dumps(wkb.loads(str(geo[0]))))
        elif geometry_format.lower() == 'wkt':
            gj[self._geometry_field] = wkb.loads(str(geo[0])).wkt


        return gj

    def get_rows(self, ogc_fid_start=0, ogc_fid_end=None, limit=50, geometry_format='geojson'):
        c = self._cursor()
        keys = self.schema()
        table = self._tablename
        geometry = self._geometry_field

        if ogc_fid_end:
            select = 'select * from {table} where OGC_FID >= {ogc_fid_start} and OGC_FID <= {ogc_fid_end};'.format(**locals())
            select2 ='select AsBinary({geometry}) from {table} where OGC_FID >= {ogc_fid_start} and OGC_FID <= {ogc_fid_end}'.format(**locals())
        elif limit > -1:
            select = 'select * from {table} where OGC_FID >= {ogc_fid_start} LIMIT {limit};'.format(
                **locals())
            select2 = 'select AsBinary({geometry}) from {table} where OGC_FID >= {ogc_fid_start} LIMIT {limit};'.format(
                **locals())
        else:
            select = 'select * from {table} where OGC_FID >= {ogc_fid_start}'.format(**locals())
            select2 = 'select AsBinary({geometry}) from {table} where OGC_FID >= {ogc_fid_start}'.format(**locals())

        c.execute("select load_extension('libspatialite.so')")
        c.execute(select)

        records = []
        for row in c.fetchall():
            records.append( dict(p for p in zip(keys, row) if p[0] != geometry) )

        c.execute(select2)
        if geometry_format.lower() == 'geojson':
            geo = [json.loads(geojson.dumps(wkb.loads(str(g[0])))) for g in c.fetchall()]
        elif geometry_format.lower() == 'wkt':
            geo = [wkb.loads(str(g[0])).wkt for g in c.fetchall()]
        else:
            geo = [None for g in c.fetchall()]

        gj = []
        for i, record in enumerate(records):
            record[self._geometry_field] = geo[i]
            gj.append(record)
            # gj.append({'type': 'feature', 'geometry': geo[i], 'properties': record})
        return gj

    def query(
            self,
            geometry_operator='overlaps',
            query_distance=False,
            query_geometry=None,
            query_mbr=None,
            query_geometry_srid=None,
            only=None,
            start=None,
            end=None,
            limit=None,
            geometry_format='geojson',
            **kwargs
    ):
        operators = {
            'eq': '=',
            '=': '=',
            'gt': '>',
            'ge': '>=',
            'lt': '<',
            'le': '<=',
            'contains': 'like',
            'startswith': 'like',
            'endswith': 'like',
            'isnull': '',
            'notnull': '',
            'ne': '!='
        }
        geom_operators = {
            'equals','disjoint','touches','within','overlaps','crosses','intersects','contains'
        }

        c = self._cursor()
        keys = self.schema() if not only else only
        table = self._tablename
        geometry = self._geometry_field
        geometry_operator = geometry_operator.lower() if geometry_operator else None

        if query_geometry and not isinstance(query_geometry, basestring):
            query_geometry = query_geometry.wkt
        elif query_mbr:
            query_mbr = shapely.geometry.box(*query_mbr)
            query_geometry = query_mbr.wkt

        limit_clause = 'LIMIT {limit}'.format(**locals()) if limit else ''
        start_clause = 'OGC_FID >= {start}'.format(**locals()) if start else False
        end_clause = 'OGC_FID >= {end}'.format(**locals()) if start else False
        columns = ','.join(keys)
        checks = [key.split('__') if '__' in key else [key, '='] for key in kwargs.keys()]
        where_clauses = ['{variable}{op}?'.format(variable=v, op=operators[o]) for v, o in checks]
        where_values = ['%' + x + '%' if checks[i][1] == 'contains' else x for i, x in enumerate(kwargs.values())]
        where_values = [x + '%' if checks[i][1] == 'startswith' else x for i, x in enumerate(kwargs.values())]
        where_values = ['%' + x if checks[i][1] == 'endswith' else x for i, x in enumerate(kwargs.values())]

        if start_clause:
            where_clauses.append(start_clause)
        if end_clause:
            where_clauses.append(end_clause)

        if query_geometry:
            qg = "GeomFromText(?, {srid})".format(srid=int(query_geometry_srid)) if query_geometry_srid else "GeomFromText(?)"
            if geometry_operator not in geom_operators and \
                    not geometry_operator.startswith('distance') and \
                    not geometry_operator.startswith('relate'):
                raise NotImplementedError('unsupported query operator for geometry')

            if geometry_operator.startswith('relate'):
                geometry_operator, matrix = geometry_operator.split(':')
                geometry_where = "relate({geometry}, {qg}, '{matrix}')"

            elif geometry_operator.startswith('distance'):
                geometry_operator, srid, comparator, val = geometry_operator.split(":")
                op = operators[comparator]
                val = float(val)
                geometry_where = "distance(transform({geometry}, {srid}), {qg}) {op} {val}".format(**locals()) if len(srid)>0 else "distance({geometry}, {qg}) {op} {val}".format(
                    **locals())
            else:
                geometry_where = "{geometry_operator}({geometry}, {qg})".format(**locals())

            where_values.append(query_geometry)
            where_clauses.append(geometry_where)

        where_clauses = ' and '.join(where_clauses)

        query1 = 'select {columns} from {table} where {where_clauses} {limit_clause}'.format(**locals())
        query2 = 'select AsBinary({geometry}) from {table} where {where_clauses} {limit_clause}'.format(**locals())
        print query1
        print where_values

        c.execute("select load_extension('libspatialite.so')")
        c.execute(query1, where_values)

        records = []
        for row in c.fetchall():
            records.append(dict(p for p in zip(keys, row) if p[0] != geometry))

        c.execute(query2, where_values)

        if geometry_format.lower() == 'geojson':
            geo = [json.loads(geojson.dumps(wkb.loads(str(g[0])))) for g in c.fetchall()]
        elif geometry_format.lower() == 'wkt':
            geo = [wkb.loads(str(g[0])).wkt for g in c.fetchall()]
        else:
            geo = [None for g in c.fetchall()]

        gj = []
        for i, record in enumerate(records):
            record[geometry] = geo[i]
            gj.append(record)

        return gj


    @classmethod
    def create_dataset(cls, title, parent, columns_definitions):
        pass

    @classmethod
    def derive_dataset(cls, title, parent_page, parent_dataresource):
        from ga_resources.models import DataResource, SpatialMetadata
        from django.conf import settings
        # create a new sqlite datasource
        slug, srs, child_spec = parent_dataresource.driver_instance.ready_data_resource()
        filename = child_spec['file']
        new_filename = parent_dataresource.driver_instance.get_filename('sqlite').split('/')[-1]
        new_filename = settings.MEDIA_ROOT + '/' + new_filename
        sh.ogr2ogr(
            '-f', 'SQLite',
            '-dsco', 'SPATIALITE=YES',
            '-t_srs', 'EPSG:3857',
            '-overwrite',
            '-skipfailures',
            new_filename, filename
        )
        ds = DataResource.objects.create(
            title=title,
            content=parent_dataresource.content,
            parent=parent_page,
            resource_file = new_filename,
            driver='ga_resources.drivers.spatialite',
            in_menus=[]
        )
        ds.driver_instance.ensure_local_file()
        ds.driver_instance.compute_fields()
        ds.driver_instance.ready_data_resource()
        return ds


    def schema(self):
        self.ready_data_resource()
        conn = self._connection()
        names = [c[0] for c in conn.cursor().execute('select * from {table} limit 1'.format(table=self._tablename)).description]
        return names

driver = SpatialiteDriver

def tests():
    from ga_resources.models import DataResource
    print 'creating resource'
    rs = DataResource.objects.create(
        title='W0607',
        content='testing...',
        resource_file='/home/th/th_cms/th_cms/test_data/W0607.sqlite',
        driver='ga_resources.drivers.spatialite'
    )
    print 'resource created'

    print 'testing driver instance'
    drv = rs.driver_instance
    print 'driver instance created'

    print 'computing spatial metadata fields'
    drv.compute_fields()
    print 'computed spatial metadata fields'

    print "computing summary"
    drv.summary()
    print "computed summary"

    print "adding column"
    drv.add_column('new_column4', 'TEXT')
    print 'added column'

    print "getting dataframe"
    df = drv.as_dataframe()
    print "got dataframe"

    print 'updating rows with column data'
    ix, row = df.iterrows().next()
    print row
    drv.update_row(row['OGC_FID'], new_column2="new value")
    print 'updated row'

    print 'deleting row'
    ix, row = df.iterrows().next()
    drv.delete_row(row['OGC_FID'])
    print 'deleted row'

    print 'deleting resource'
    rs.delete()





