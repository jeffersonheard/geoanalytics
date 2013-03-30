from lxml import etree
import mapnik
from collections import OrderedDict
from hashlib import md5
from ga_resources import models as m
import importlib
import os
from osgeo import osr
from django.conf import settings as s
import sh

def prepare_wms(layers, srs, styles, bgcolor=None, transparent=None, **kwargs):
    # FIXME this only occurs once.  We have to delete the style files associated with the stylenames somehow.

    d = OrderedDict(layers=layers, srs=srs, styles=styles, bgcolor=bgcolor, transparent=transparent)
    shortname = md5()
    for key, value in d.items():
        shortname.update(key)
        shortname.update(unicode(value))
    cache_entry_basename = shortname.hexdigest()
    cache_path = os.path.join(s.MEDIA_ROOT, '.cache', '_cached_layers')

    if not os.path.exists(cache_path):
        os.makedirs(cache_path) # just in case it's not there yet.

    cache_path = os.path.join(cache_path, cache_entry_basename)

    layer_specs = []
    for layer in layers:
        rendered_layer = m.RenderedLayer.objects.get(slug=layer)
        resource_slug = rendered_layer.data_resource.slug
        driver = importlib.import_module(rendered_layer.data_resource.driver)
        layer_path, layer_spec = driver.ready_data_resource(resource_slug, **kwargs)
        layer_specs.append(layer_spec)

    if not os.path.exists(cache_path + ".xml"):
        stylesheets = [m.Style.objects.get(slug=style).stylesheet for style in styles]
        try:
            compile_mapfile(cache_path, srs, stylesheets, *layer_specs)
        except sh.ErrorReturnCode_1, e:
            raise RuntimeError(str(e.stderr))

    return cache_path


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
    map = etree.Element('map')
    map.set("srs", srs)
    for stylesheet in stylesheets:
        # etree.SubElement(map, "Stylesheet").text = open(stylesheet).read()
        etree.SubElement(map, "Stylesheet").text = stylesheet
    for layer_id, lsrs, parms in layers:
        compile_layer(map, layer_id, lsrs, **parms)
    return map

def compile_mapfile(name, srs, stylesheets, *layers):
    with open(name + ".mml", 'w') as mapfile:
        mapfile.write(etree.tostring(compile_mml(srs, stylesheets, *layers), pretty_print=True))
    sh.cascadenik(name + '.mml', name + '.xml')


def render(fmt, width, height, bbox, srs, styles, layers, **kwargs):
    if srs.lower().startswith('epsg'):
        if srs.endswith("900913"):
            srs = srs[:-6] + '3857'
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

