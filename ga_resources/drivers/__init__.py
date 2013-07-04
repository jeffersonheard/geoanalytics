import json
from django.utils.timezone import utc
from lxml import etree
import mapnik
from collections import OrderedDict
from hashlib import md5
from ga_resources import models as m
import os
from django.conf import settings as s
import sh
from datetime import datetime
from urllib2 import urlopen
import requests
import re
from django.conf import settings
from ga_resources import predicates

VECTOR = False
RASTER = True


class Driver(object):
    """Abstract class that defines a number of reusable methods to load geographic data and create services from it"""
    def __init__(self, data_resource):
        self.resource = data_resource
        self.cache_path = self.resource.cache_path
        self.cached_basename = os.path.join(self.cache_path, os.path.split(self.resource.slug)[-1])

    def ensure_local_file(self, freshen=False):
        if self.resource.resource_file:
            _, ext = os.path.splitext(self.resource.resource_file.name)
        elif self.resource.resource_url:
            _, ext = os.path.splitext(self.resource.resource_url)
        else:
            return None

        cached_filename = self.cached_basename + ext
        self.src_ext = ext

        ready = self.resource.perform_caching and os.path.exists(cached_filename) and not freshen

        if not ready:
            if self.resource.resource_file:
                if os.path.exists(cached_filename):
                    os.unlink(cached_filename)
                os.symlink(os.path.join(s.MEDIA_ROOT, self.resource.resource_file.name), cached_filename)
            elif self.resource.resource_url:
                if self.resource.resource_url.startswith('ftp'):
                    result = urlopen(self.resource.resource_url).read()
                    if result:
                        with open(cached_filename, 'wb') as resource_file:
                            resource_file.write(result)
                else:
                    result = requests.get(self.resource.resource_url)
                    if result.ok:
                        with open(cached_filename, 'wb') as resource_file:
                            resource_file.write(result.content)
            return True
        else:
            return False

    def supports_download(self):
        return True

    def filestream(self):
        self.ensure_local_file()
        return open(self.cached_basename + self.src_ext)

    def mimetype(self):
        return "application/octet-stream"

    def ready_data_resource(self, **kwargs):
        """This should return the path to a data file or directory containing a resource that can be read by Mapnik.  Returns a layer spec that goes into compile_layer"""
        raise NotImplementedError("Method ready_data_resource not implemented in abstract class")

    def compute_fields(self, **kwargs):
        self.ensure_local_file()

        filehash = md5()
        with open(self.cached_basename + self.src_ext) as f:
            b = f.read(10 * 1024768)
            while b:
                filehash.update(b)
                b = f.read(10 * 1024768)

        md5sum = filehash.hexdigest()
        if md5sum != self.resource.md5sum:
            self.resource.md5sum = md5sum
            self.resource.last_change = datetime.utcnow().replace(tzinfo=utc)

    def get_metadata(self, **kwargs):
        """If there is metadata conforming to some standard, then return it here"""
        return {}

    def get_data_fields(self, **kwargs):
        """If this is a shapefile, return the names of the fields in the DBF and their datattypes.  If this is a data
        raster (as opposed to an RGB or grayscale raster, return the names of the bands or subdatasets and their
        datatypes."""
        return []

    def get_filename(self, xtn):
        filename = os.path.split(self.resource.slug)[-1]
        return os.path.join(self.cache_path, filename + '.' + xtn)

    def get_data_for_point(self, wherex, wherey, srs, fuzziness=0, **kwargs):
        raise NotImplementedError("Method get_data_for_point is not implemented in abstract class")

    def as_dataframe(self, **kwargs):
        raise NotImplementedError("This driver does not support dataframes")

    def summary(self, **kwargs):
        df = self.as_dataframe(**kwargs)
        keys = [k for k in df.keys() if k != 'geometry']
        type_table = {
            'float64': 'number',
            'int64': 'number',
            'object': 'text'
        }

        ctx = [{'name': k} for k in keys]
        for i, k in enumerate(keys):
            s = df[k]
            ctx[i]['kind'] = type_table[s.dtype.name]
            ctx[i]['tags'] = [tag for tag in [
                'unique' if predicates.unique(s) else None,
                'not null' if predicates.not_null(s) else None,
                'null' if predicates.some_null(s) else None,
                'empty' if predicates.all_null(s) else None,
                'categorical' if predicates.categorical(s) else None,
                'open ended' if predicates.continuous(s) else None,
                'mostly null' if predicates.mostly_null(s) else None,
                'uniform' if predicates.uniform(s) else None
            ] if tag]
            if 'categorical' in ctx[i]['tags']:
                ctx[i]['uniques'] = [x for x in s.unique()]
            for k, v in s.describe().to_dict().items():
                ctx[i][k] = v

        return ctx

#
# See below.  I switched this to Carto, which requires JSON files instead of XML.
#
#def compile_layer(parent, layer_id, srs, **parameters):
#    layer = etree.SubElement(parent, "Layer")
#    layer.set("id", layer_id)
#    layer.set("srs", srs)
#    ds = etree.SubElement(layer, 'Datasource')
#
#    for name, value in parameters.items():
#        p = etree.SubElement(ds, 'Parameter')
#        p.set("name", name)
#        p.text = value
#    return layer

#def compile_mml(srs, stylesheets, *layers):
#    mapfile = etree.Element('Map')
#    mapfile.set("srs", srs)
#    for stylesheet in stylesheets:
#        # etree.SubElement(map, "Stylesheet").text = open(stylesheet).read()
#        etree.SubElement(mapfile, "Stylesheet").text = stylesheet
#    for layer_id, lsrs, parms in layers:
#        compile_layer(mapfile, layer_id, lsrs, **parms)
#    return mapfile

#def compile_mapfile(name, srs, stylesheets, *layers):
#    with open(name + ".mml", 'w') as mapfile:
#        mapfile.write(etree.tostring(compile_mml(srs, stylesheets, *layers), pretty_print=True))
#    sh.cascadenik(name + '.mml', name + '.xml')


def compile_layer(layer_id, srs, **parameters):
    return {
        "id" : re.sub('/', '_', layer_id),
        "name" : re.sub('/', '_', layer_id),
        "srs" : srs,
        "Datasource" : parameters
    }

def compile_mml(srs, stylesheets, *layers):
    mml = {
        'srs' : srs,
        'Stylesheet' : [{ "id" : re.sub('/', '_', stylesheet.slug), "data" : stylesheet.stylesheet} for stylesheet in stylesheets],
        'Layer' : [compile_layer(layer_id, lsrs, **parms) for layer_id, lsrs, parms in layers]
    }
    return mml


def compile_mapfile(name, srs, stylesheets, *layers):
    with open(name + ".mml", 'w') as mapfile:
        mapfile.write(json.dumps(compile_mml(srs, stylesheets, *layers), indent=4))
    carto = sh.Command(settings.CARTO_HOME + "/bin/carto")
    carto(name + '.mml', _out=name + '.xml')


def prepare_wms(layers, srs, styles, bgcolor=None, transparent=None, **kwargs):
    d = OrderedDict(layers=layers, srs=srs, styles=styles, bgcolor=bgcolor, transparent=transparent)
    shortname = md5()
    for key, value in d.items():
        shortname.update(key)
        shortname.update(unicode(value))
    cache_entry_basename = shortname.hexdigest()
    cache_path = os.path.join(s.MEDIA_ROOT, '.cache', '_cached_layers')
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)  # just in case it's not there yet.

    cached_filename = os.path.join(cache_path, cache_entry_basename)
    for style in styles:
        s.WMS_CACHE_DB.sadd(style, cached_filename)
    for layer in layers:
        s.WMS_CACHE_DB.sadd(layer, cached_filename)

    layer_specs = []
    for layer in layers:
        rendered_layer = m.RenderedLayer.objects.get(slug=layer)
        driver = rendered_layer.data_resource.driver_instance
        _, layer_spec = driver.ready_data_resource(**kwargs)
        layer_specs.append(layer_spec)

    stylesheet_objects = [m.Style.objects.get(slug=style) for style in styles]
    if not os.path.exists(cached_filename + ".xml"):  # not an else as previous clause may remove file.
        stylesheets = [style for style in stylesheet_objects]
        try:
            compile_mapfile(cached_filename, srs, stylesheets, *layer_specs)
        except sh.ErrorReturnCode_1, e:
            raise RuntimeError(str(e.stderr))

    return cached_filename


def render(fmt, width, height, bbox, srs, styles, layers, **kwargs):
    if srs.lower().startswith('epsg'):
        if srs.endswith("900913") or srs.endswith("3857"):
            srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null"
        else:
            srs = "+init=" + srs.lower()

    name = prepare_wms(layers, srs, styles, **kwargs)
    filename = md5()

    filename.update("{bbox}.{width}x{height}".format(
        name=name,
        bbox=','.join(str(b) for b in bbox),
        width=width,
        height=height,
        fmt=fmt
    ))
    filename = name + filename.hexdigest() + '.' + fmt

    if os.path.exists(filename):
        return filename
    else:
        m = mapnik.Map(width, height)
        mapnik.load_map(m, name + '.xml')
        m.zoom_to_box(mapnik.Box2d(*bbox))
        mapnik.render_to_file(m, filename, fmt)

    return filename

