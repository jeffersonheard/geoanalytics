from lxml import etree
import mapnik
from collections import OrderedDict
from hashlib import md5
from ga_resources import models as m
import os
from django.conf import settings as s
import sh
from datetime import datetime
from django.utils.timezone import utc

class Driver(object):
    """Abstract class that defines a number of reusable methods to load geographic data and create services from it"""
    def __init__(self, data_resource):
        self.resource = data_resource
        self.cache_path = os.path.join(s.MEDIA_ROOT, ".cache", "resources", *os.path.split(self.resource.slug))

        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)


    def ready_data_resource(self, **kwargs):
        """This should return the path to a data file or directory containing a resource that can be read by Mapnik.  Returns a layer spec that goes into compile_layer"""
        raise NotImplementedError("Method ready_data_resource not implemented in abstract class")

    def compute_fields(self, **kwargs):
        raise NotImplementedError("Method compute_fields not implemented in abstract class")

    def get_metadata(self, **kwargs):
        """If there is metadata conforming to some standard, then return it here"""
        return {}

    def get_data_fields(self, **kwargs):
        """If this is a shapefile, return the names of the fields in the DBF and their datattypes.  If this is a data
        raster (as opposed to an RGB or grayscale raster, return the names of the bands or subdatasets and their
        datatypes."""
        return []

    def get_data_for_point(self, wherex, wherey, srs, fuzziness=0, **kwargs):
        raise NotImplementedError("Method get_data_for_point is not implemented in abstract class")

def compile_layer(parent, layer_id, srs, **parameters):
    layer = etree.SubElement(parent, "Layer")
    layer.set("id", layer_id)
    layer.set("srs", srs)
    ds = etree.SubElement(layer, 'Datasource')

    for name, value in parameters.items():
        p = etree.SubElement(ds, 'Parameter')
        p.set("name", name)
        p.text = value
    return layer

def compile_mml(srs, stylesheets, *layers):
    mapfile = etree.Element('Map')
    mapfile.set("srs", srs)
    for stylesheet in stylesheets:
        # etree.SubElement(map, "Stylesheet").text = open(stylesheet).read()
        etree.SubElement(mapfile, "Stylesheet").text = stylesheet
    for layer_id, lsrs, parms in layers:
        compile_layer(mapfile, layer_id, lsrs, **parms)
    return mapfile

def compile_mapfile(name, srs, stylesheets, *layers):
    with open(name + ".mml", 'w') as mapfile:
        mapfile.write(etree.tostring(compile_mml(srs, stylesheets, *layers), pretty_print=True))
    sh.cascadenik(name + '.mml', name + '.xml')


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

    cache_path = os.path.join(cache_path, cache_entry_basename)

    layer_specs = []
    cache_seconds = 2**31
    for layer in layers:
        rendered_layer = m.RenderedLayer.objects.get(slug=layer)
        cache_seconds = min(rendered_layer.cache_seconds, cache_seconds)
        driver = rendered_layer.data_resource.driver_instance
        _, layer_spec = driver.ready_data_resource(**kwargs)
        layer_specs.append(layer_spec)

    stylesheet_objects = [m.Style.objects.get(slug=style) for style in styles]
    if os.path.exists(cache_path + ".xml"):
        newest_date = max(style.publish_date for style in stylesheet_objects)
        xml_date = datetime.utcfromtimestamp(os.stat(cache_path + ".xml").st_mtime).replace(tzinfo=utc)
        if xml_date < newest_date:
            sh.rm(sh.glob(cache_path + "*"))

    if not os.path.exists(cache_path + ".xml"):  # not an else as previous clause may remove file.
        stylesheets = [style.stylesheet for style in stylesheet_objects]
        try:
            compile_mapfile(cache_path, srs, stylesheets, *layer_specs)
        except sh.ErrorReturnCode_1, e:
            raise RuntimeError(str(e.stderr))

    return cache_path


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
    m = mapnik.Map(width, height)
    mapnik.load_map(m, name + '.xml')
    m.zoom_to_box(mapnik.Box2d(*bbox))
    mapnik.render_to_file(m, filename, fmt)

    return filename

