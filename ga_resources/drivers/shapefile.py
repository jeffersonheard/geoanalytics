# from ga_ows.views import wms, wfs
from django.conf import settings as s
import os
import sh
from ga_resources import models as m
import mapnik
import time
import requests
import urllib
from collections import OrderedDict
from lxml import etree
from osgeo import osr

VECTOR = False
RASTER = True

DATA_TYPE = VECTOR

def ready_data_resource(layer, **kwargs):
    """Other keyword args get passed in as a matter of course, like BBOX, time, and elevation, but this basic driver
    ignores them"""

    resource = m.DataResource.objects.get(slug=layer)
    cache_path = os.path.join(s.MEDIA_ROOT, ".cache", "resources", resource.slug)
    os.makedirs(cache_path)

    if resource.resource_file:
        _, ext = os.path.splitext(resource.resource_file.name)[-1]
    elif resource.resource_url:
        _, ext = os.path.splitext(resource.resource_url)
    else:
        _, ext = os.path.splitext(resource.resource_irods_file)

    cached_basename = os.path.join(cache_path, resource.slug)
    cached_filename = cached_basename + '.' + ext

    ready = False
    if resource.perform_caching and os.path.exists(cached_filename):
        mtime = os.stat(cache_path).st_mtime
        now = time.time()
        if now - mtime < resource.cache_ttl:
            ready = True

    if not ready:
        if resource.resource_file:
            os.symlink(resource.resource_file.name, cached_filename)
        elif resource.resource_url:
            result = requests.get(resource.resource_url)
            ext = resource.resource_url.split('.')[-1]
            if result.ok:
                with open(cached_filename, 'wb') as resource_file:
                    resource_file.write(result.content)
        elif resource.resource_irods_file:
            pass # TODO figure out how to best support IRODS. I'd rather not copy large resources.

        if ext == 'zip':
            sh.unzip(cached_filename)
            sh.mv('*.shp', cached_basename + '.shp')
            sh.mv('*.shx', cached_basename + '.shx')
            sh.mv('*.dbf', cached_basename + '.dbf')
            sh.mv('*.prj', cached_basename + '.prj')
            sh.mv('*.aux.xml', cached_basename + '.aux.xml')

    return cache_path

def prepare_request(layers, srs, styles, bgcolor, transparent, **kwargs):
    # TODO bgcolor unsupported.  Things are always transparent
    # TODO this can be made general.  All we really need to do is make each individual layer tell us what driver it's using for mapnik.

    d = OrderedDict(layers=layers, srs=srs, styles=styles, bgcolor=bgcolor, transparent=transparent)
    cache_entry_basename = urllib.urlencode(d)
    cache_path = os.path.join(s.MEDIA_ROOT, '.cache', '_cached_layers')
    os.makedirs(cache_path) # just in case it's not there yet.
    cache_path = os.path.join(cache_path, cache_entry_basename)

    layer_specs = []
    for layer in layers:
        layer_path = ready_data_resource(layer)
        with open(os.path.join(layer_path, layer + '.prj')) as f:
            srs = osr.SpatialReference()
            srs.ImportFromWkt(f.read())
            srs = srs.ExportToProj4()
        layer_specs.append((layer, srs, {'type': 'shape', "file": os.path.join(layer_path, layer + '.shp')}))

    if not os.path.exists(cache_path + ".xml"):
        stylesheets = [m.Style.objects.get(style).stylesheet_filename for style in styles]
        try:
            compile_mapfile(cache_entry_basename, srs, stylesheets, *layer_specs)
        except sh.ErrorReturnCode_1, e:
            raise RuntimeError(str(e.stderr))

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

def compile_mml(srs, stylesheet_files, *layers):
    map = etree.Element('map')
    map.set("srs", srs)
    for stylesheet in stylesheet_files:
        # etree.SubElement(map, "Stylesheet").text = open(stylesheet).read()
        etree.SubElement(map, "Stylesheet").set('src',stylesheet)
    for layer_id, lsrs, parms in layers:
        compile_layer(map, layer_id, lsrs, **parms)
    return map

def compile_mapfile(name, srs, stylesheets, *layers):
    with open(name + ".mml", 'w') as mapfile:
        mapfile.write(etree.tostring(compile_mml(srs, stylesheets, *layers), pretty_print=True))
        sh.cascadenik(name + '.mml', name + '.xml')

def render(outfile, format, width, height, bbox, srs, stylesheets, layers, refresh=True):
    m = mapnik.Map(width, height)

    if refresh or not os.path.exists(outfile + '.xml'):
        compile_mapfile(outfile, srs, stylesheets, *layers)

    mapnik.load_map(m, outfile + '.xml')
    m.zoom_to_box(mapnik.Box2d(*bbox))
    mapnik.render_to_file(m, outfile + '.' + format, format)

