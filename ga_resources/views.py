from zipfile import ZipFile
from django.contrib.gis.geos import Polygon, GEOSGeometry
from ga_ows.views import wfs, wms
from ga_resources import models, drivers
import json
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, Http404
from ga_resources.drivers import shapefile
from ga_resources.models import DataResource
from osgeo import osr, ogr
import importlib
from mezzanine.pages.models import Page
from mezzanine.utils.urls import admin_url
from django.shortcuts import get_object_or_404
from hashlib import md5

def kmz_resource(request, *args, **kwargs):
    slug = kwargs['slug']
    ff = kwargs['filename']
    ds = get_object_or_404(DataResource, slug=slug)

    if ds.driver != 'ga_resources.drivers.kmz':
        raise Http404(slug)
    else:
        _, _, cfg = ds.driver_instance.ready_data_resource(*args, **kwargs)

        try:
            return HttpResponse(ds.driver_instance.open_stream(ff), mimetype='application/x-binary')
        except Exception, e:
            raise Http404(str(e))

def kmz_features(request, *args, **kwargs):
    slug = kwargs['slug']
    ds = get_object_or_404(DataResource, slug=slug)

    if ds.driver != 'ga_resources.drivers.kmz':
        raise Http404(slug)
    else:
        _, _, cfg = ds.driver_instance.ready_data_resource(*args, **kwargs)
        return HttpResponse(ds.driver_instance.features(), mimetype='application/vnd.google-earth.kml+xml')

def kmz_ground_overlays_json(request, *args, **kwargs):
    slug = kwargs['slug']
    ds = get_object_or_404(DataResource, slug=slug)

    if ds.driver != 'ga_resources.drivers.kmz':
        raise Http404(slug)
    else:
        _, _, cfg = ds.driver_instance.ready_data_resource(*args, **kwargs)
        ground_overlays = ds.driver_instance.ground_overlays()
        for i, g in enumerate(ground_overlays):
            ground_overlays[i]['href'] = '/ga_resources/kmz-resource/{slug}:{href}'.format(slug=slug, href=ground_overlays[i]['href'])
        return HttpResponse(json.dumps(ground_overlays, indent=4), mimetype='application/javascript')


def create_page(request):
    models = request.GET['module']
    pageclass = request.GET['classname']
    parent = request.GET['parent']

    parent = Page.objects.get(slug=parent).get_content_model()
    models = importlib.import_module(models)
    pageclass = getattr(models, pageclass)

    title = request.GET.get('title', "new " + pageclass._meta.object_name)
    # page = pageclass.objects.create(title=title, parent=parent)
    return HttpResponseRedirect(admin_url(pageclass, 'add') + "?parent={pk}&next={next}".format(pk=parent.pk, next=parent.get_absolute_url()))

def delete_page(request):
    slug = request.GET['slug']
    p = Page.objects.get(slug=slug)
    to = p.parent if p.parent else '/'
    p.delete()
    return HttpResponseRedirect(to.get_absolute_url())

def download_file(request, *args, **kwargs):
    slug, ext = kwargs['slug'].split('.')
    drv = get_object_or_404(DataResource, slug=slug)
    if drv.driver_instance.supports_download():
        rsp = HttpResponse(drv.driver_instance.filestream(), mimetype=drv.driver_instance.mimetype())
        rsp['Content-Disposition'] = 'attachment; filename="{filename}"'.format(filename=drv.slug.split('/')[-1] + '.' + ext)
        return rsp
    else:
        return HttpResponseNotFound()

def extent(request, *args, **kwargs):

    res = DataResource.objects.get(slug=kwargs['slug'])
    ret = res.spatial_metadata.bounding_box
    ret.transform(int(request.REQUEST.get('srid', 3857)))
    ret = ret.extent

    callback = None
    if 'jsonCallback' in request.REQUEST:
        callback = request.REQUEST['jsonCallback']
    elif 'callback' in request.REQUEST:
        callback = request.REQUEST['callback']

    if callback:
        return HttpResponse(callback + '(' + json.dumps(ret) + ")", mimetype='text/plain')
    else:
        return HttpResponse(json.dumps(ret), mimetype='application/json')


def search_catalog(request, *args, **kwargs):
    """A spatial search for the DataResource catalog. In the future, this will be more thorough, but right now it looks
    for a filter parameter in the request, and inside that a JSON payload including a bbox four-tuple of minx, maxx
     miny, maxy OR a geometry wkt and an optional srid.  It then performs a broad overlap search and returns the results
     as a JSON or JSONP list of::

        [{ "title" : "title",
           "path" : ["breadcrumps", "to", "resource"],
           "url" : "http://mydomain/ga_resources/path/to/resource/title"
        }]
    """
    flt = json.loads(request.REQUEST['filter'])
    if 'bbox' in flt:
        minx, miny, maxx, maxy = flt['bbox']
        geometry = Polygon.from_bbox((minx, miny, maxx, maxy))
    else:
        geometry = GEOSGeometry(flt['boundary'])

    if 'srid' in flt:
        geometry.set_srid(flt['srid'])

    results = models.SpatialMetadata.objects.filter(geometry__overlaps=geometry)
    ret = [{ 'title' : r.title, 'path' : r.slug.split('/')[:-1], 'url' : r.get_abolute_url() } for r in results]

    callback = None
    if 'jsonCallback' in request.REQUEST:
        callback = request.REQUEST['jsonCallback']
    elif 'callback' in request.REQUEST:
        callback = request.REQUEST['callback']

    if callback:
        return HttpResponse(callback + '(' + json.dumps(ret) + ")", mimetype='text/plain')
    else:
        return HttpResponse(json.dumps(ret), mimetype='application/json')


class WMSAdapter(wms.WMSAdapterBase):
    def layerlist(self):
        return [l.slug for l in models.RenderedLayer.objects.all()]

    def get_2d_dataset(self, layers, srs, bbox, width, height, styles, bgcolor, transparent, time, elevation, v, filter, **kwargs):
        """use the driver to render a tile"""
        return open(drivers.render(kwargs['format'], width, height, bbox, srs, styles, layers, **kwargs))

    def get_feature_info(self, wherex, wherey, layers, callback, format, feature_count, srs, filter, fuzziness=0, **kwargs): # fuzziness of 30 meters by default
        """use the driver to get feature info"""

        if srs.lower().startswith('epsg'):
           s = osr.SpatialReference()
           s.ImportFromEPSG(int(srs[5:]))
           srs = s.ExportToProj4()

        feature_info = {
            layer : models.RenderedLayer.objects.get(slug=layer).data_resource.driver_instance.get_data_for_point(
                wherex, wherey, srs, fuzziness=fuzziness, **kwargs
            )
        for layer in layers }

        return feature_info

    def nativesrs(self, layer):
        """Use the resource record to get native SRS"""
        resource = models.RenderedLayer.objects.get(slug=layer).data_resource
        return resource.spatial_metadata.native_srs

    def nativebbox(self, layer=None):
        """Use the resource record to get the native bounding box"""
        if layer:
            resource = models.RenderedLayer.objects.get(slug=layer).data_resource
            return resource.spatial_metadata.native_bounding_box.extent
        else:
            return (-180,-90,180,90)

    def styles(self):
        """Use the resource record to get the available styles"""
        return list(models.Style.objects.all())

    def get_layer_descriptions(self):
        """
        This should return a list of dictionaries.  Each dictionary should follow this format::
            { ""name"" : layer_"name",
              "title" : human_readable_title,
              "srs" : spatial_reference_id,
              "queryable" : whether or not GetFeatureInfo is supported for this layer,
              "minx" : native_west_boundary,
              "miny" : native_south_boundary,
              "maxx" : native_east_boundary,
              "maxy" : native_north_boundary,
              "ll_minx" : west_boundary_epsg4326,
              "ll_miny" : south_boundary_epsg4326,
              "ll_maxx" : east_boundary_epsg4326,
              "ll_maxy" : north_boundary_epsg4326,
              "styles" : [list_of_style_descriptions]

        Each style description in list_of_style_descriptions should follow this format::
            { ""name"" : style_"name",
              "title" : style_title,
              "legend_width" : style_legend_width,
              "legend_height" : style_legend_height,
              "legend_url" : style_legend_url
            }
        """
        layers = models.RenderedLayer.objects.all()
        ret = []
        for layer in layers:
            desc = {}
            ret.append(desc)
            desc["name"] = layer.slug
            desc['title'] = layer.title
            desc['srs'] = layer.data_resource.spatial_metadata.native_srs
            desc['queryable'] = True
            desc['minx'], desc['miny'], desc['maxx'], desc['maxy'] = layer.data_resource.spatial_metadata.native_bounding_box.extent  # FIXME this is not native
            desc['ll_minx'], desc['ll_miny'], desc['ll_maxx'], desc['ll_maxy'] = layer.data_resource.spatial_metadata.bounding_box.extent
            desc['styles'] = []
            desc['styles'].append({
                "name" : layer.default_style.slug,
                'title' : layer.default_style.title,
                'legend_width' : layer.default_style.legend_width,
                'legend_height' : layer.default_style.legend_height,
                'legend_url' : layer.default_style.legend.url if layer.default_style.legend else ""
            })
            for style in layer.styles.all():
                desc['styles'].append({
                    "name" : style.slug,
                    'title' : style.title,
                    'legend_width' : style.legend_width,
                    'legend_height' : style.legend_height,
                    'legend_url' : style.legend.url if style.legend else ""
                })
        return ret


    def get_service_boundaries(self):
        """Just go ahead and return the world coordinates"""

        return {
          "minx" : -180.0,
          "miny" : -90.0,
          "maxx" : 180.0,
          "maxy" : 90.0
        }

class WMS(wms.WMS):
    adapter = WMSAdapter([])

class WFSAdapter(wfs.WFSAdapter):
    def get_feature_descriptions(self, request, *types):
        namespace = request.build_absolute_uri().split('?')[0] + "/schema" # todo: include https://bitbucket.org/eegg/django-model-schemas/wiki/Home

        for type_name in types:
            res = get_object_or_404(models.DataResource, slug=type_name)

            yield wfs.FeatureDescription(
                ns=namespace,
                ns_name='ga_resources',
                name=res.slug,
                abstract=res.description,
                title=res.title,
                keywords=res.keywords,
                srs=res.spatial_metadata.native_srs,
                bbox=res.spatial_metadata.bounding_box,
                schema=namespace + '/' + res.slug
            )

    def list_stored_queries(self, request):
        """list all the queries associated with drivers"""
        sq = super(WFSAdapter, self).list_stored_queries(request)
        return sq

    def get_features(self, request, parms):
        if parms.cleaned_data['stored_query_id']:
            squid = "SQ_" + parms.cleaned_data['stored_query_id']
            slug = parms.cleaned_data['type_names'] if isinstance(parms.cleaned_data['type_names'], basestring) else parms.cleaned_data['type_names'][0]
            try:
                return models.DataResource.driver_instance.query_operation(squid)(request, **parms.cleaned_data)
            except:
                raise wfs.OperationNotSupported.at('GetFeatures', 'stored_query_id={squid}'.format(squid=squid))
        else:
            return self.AdHocQuery(request, **parms.cleaned_data)

    def AdHocQuery(self, req,
       type_names=None,
       filter=None,
       filter_language=None,
       bbox=None,
       sort_by=None,
       count=None,
       start_index=None,
       srs_name=None,
       srs_format=None,
       max_features=None,
       **kwargs
    ):
        model = get_object_or_404(models.DataResource, slug=type_names[0])
        driver = model.driver_instance

        extra = {}
        if filter:
            extra['filter'] = json.loads(filter)

        if bbox:
            extra['bbox'] = bbox

        if srs_name:
            srs = osr.SpatialReference()
            if srs_name.lower().startswith('epsg'):
                srs.ImportFromEPSG(int(srs_name[5:]))
            else:
                srs.ImportFromProj4(srs_name)
            extra['srs'] = srs
        else:
            srs = model.srs

        if start_index:
            extra['start'] = start_index

        count = count or max_features
        if count:
            extra['count'] = count

        if "boundary" in kwargs:
            extra['boundary'] = kwargs['boundary']
            extra['boundary_type'] = kwargs['boundary_type']

        df = driver.as_dataframe(**extra)

        if sort_by:
            extra['sort_by'] = sort_by

        if filter_language and filter_language != 'json':
            raise wfs.OperationNotSupported('filter language must be JSON for now')

        filename = md5()

        filename.update("{name}.{bbox}.{srs_name}x{filter}".format(
            name=type_names[0],
            bbox=','.join(str(b) for b in bbox),
            srs_name=srs_name,
            filter=filter
        ))
        filename = filename.hexdigest()
        shapefile.ShapefileDriver.from_dataframe(df, filename, srs)
        ds = ogr.Open(filename)
        return ds

    def supports_feature_versioning(self):
        return False

class WFS(wfs.WFS):
    adapter=WFSAdapter()

