from bson import Binary
from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
from lxml import etree

try:
    import scipy.misc
    HAVE_SCIPY = True
except ImportError:
    HAVE_SCIPY = False

try:
    import cairo
    HAVE_CAIRO = True
except ImportError:
    HAVE_CAIRO = False

from datetime import datetime
from cStringIO import StringIO
import pymongo
import hashlib

from osgeo import gdal
import tempfile

from ga_ows import utils
from ga_ows.views import common
import django.forms as f
from django.conf import settings

class WMSCache(object):
    """The WMS Cache, based on MongoDB.

    Public Members:

    * self.collection : the PyMongo collection object.  See the PyMongo API for how to use this.
    """
    def __init__(self, route='default', collection='wms_cache', *locators):
        """
        :param route: The MongoDB route as listed in settings.MONGODB_ROUTES
        :param collection: The Mongo collection to use for this cache
        :param locators: Locator keys that need to be indexed to find items by something other than primary key.
        :return:
        """

        #: ..

        if not hasattr(settings, 'MONGODB_ROUTES'):
            raise EnvironmentError('Settings must contain MONGODB_ROUTES')

        if route in settings.MONGODB_ROUTES:
            self.collection = settings.MONGODB_ROUTES[route][collection]
        else:
            self.collection = settings.MONGODB_ROUTES['default'][collection]

        self.collection.ensure_index([("_creation_time", pymongo.DESCENDING)])
        self.collection.ensure_index([("_used_time", pymongo.DESCENDING)])

    def save(self, item, **keys):
        """ Save or update a cache item.
        :param item: The item to save.
        :param keys: The keys to save the item under.  Must be serializable by PyMongo.
        :return:
        """
        document = keys
        docid = hashlib.new('md5')
        docid.update(str(sorted(keys.items())))
        docid = docid.hexdigest()

        document['_id'] = docid
        document['_item'] = Binary(item)
        document['_creation_time'] = datetime.utcnow()
        document['_used_time'] = document['_creation_time']
        self.collection.save(document)

    def locate(self, **keys):
        """ Find a single item in the cache.
        :param keys:
        :return:
        """
        docid = hashlib.new("md5")
        docid.update(str(sorted(keys.items())))
        docid = docid.hexdigest()

        item = self.collection.find_and_modify({ '_id' : docid }, {"$set" : {'_used_time' : datetime.utcnow() }})
        if item:
            return item['_item']
        else:
            return None

    def collect(self, **keys):
        """ Find all the items that match particular keys in the cache.
        :param keys: A list of keys.
        :return:
        """
        return self.collection.find(keys)

    def flush(self):
        """
        Delete the cache entirely.
        """
        self.collection.drop()

    def flush_older(self, when, **kwargs):
        """
        Delete cache entries older than a given time that also match a set of criteria.

        :param when: A datetime object in the same time zone as the objects in the cache (prefer UTC)
        :param kwargs: A set of pymongo query descriptors.  See `http://mongodb.org`_ for more details.
        """
        kwargs['_creation_time'] = {'$lte', when }
        self.collection.remove(kwargs)

    def flush_lru(self, count):
        """
        Flush the least-recently-used keys in the cache until there are no more than [count] objects in the cache

        :param count: The cap of the number of remaining objects in the cache.
        """
        total = self.collection.count()
        if total > count:
            key = self.collection.find().sort(('_used_time', pymongo.DESCENDING))[count]
            key = key['_used_time']
            self.collection.remove({ '_used_time' : {'$lte' : key}})

    @staticmethod
    def for_geodjango_model(model, route='default'):
        """Return a specialized instance for a GeoDjango model.
        :param model: The model class itself
        :param route: The MongoDB route to use.
        :return: A WMSCache object specialized to a GeoDjango model
        """
        return WMSCache(route, model._meta.app_label + "_" + model._meta.module_name + "__wms_cache", "model")

    class GeoDjangoCacheInvalidatingignalHandler(object):
        """ When connected to Django's post_save signal, this invalidates the WMS cache for a model when an instance of a
            model class is saved, created, or updated. Usage is similar to::

                from django.signals import post_save, post_delete, m2m_changed

                handler = WMSCache.GeoDjangoCacheInvalidatingSignalHandler(models.CensusCounty)
                post_save.connect(handler)
                post_delete.connect(handler)
                m2m_changed.connect(handler)

            This is a fairly blunt instrument.  A better signal handler would actually look for the bounding boxes of the
            cached tiles and find all the tiles that actually change due to the modification of the database.  However,
            this will work.
        """
        def __init__(self, model, cache=None):
            """
            :param model: The sender model to invalidate
            :param cache: The cache instance that contains the instances
            :return:
            """
            self.looking_for = model
            if cache:
                self.cache = cache
            else:
                self.cache = WMSCache.for_geodjango_model(model)

        def __call__(self, sender, **kwargs):
            if sender == self.looking_for:
                self.cache.collect(model=sender._meta.object_name).remove()


class WMSAdapterBase(object):
    """ An abstract base-class for adapting a data model to the WMS implementation given in this module.
    """
    cache = None

    def __init__(self, styles, requires_time=False, requires_elevation=False, requires_version=False):
        self.styles = styles
        self.requires_time = requires_time
        self.requires_elevation = requires_elevation
        self.requires_version = requires_version

    def cache_result(self, item, **kwargs):
        """Cache away the result of a WMS render.
        :param item: The item to cache.  Should be a binary image
        :param kwargs:
        :return:
        """

    def get_cache_record(self, layers, srs, bbox, width, height, styles, format, bgcolor, transparent, time, elevation, v, filter, **kwargs):
        """ Get the cache record for a set of parameters
        :return: The item that was cached.  Will be a binary image.
        """
        return None

    def get_valid_elevations(self, **kwargs):
        """ Get valid elevations for the specified query.
        :param kwargs:  All the keyword arguments that would normally be valid for a GetMap request.  See ga_ows.common.GetValidElevationsMixin.

        :return: A JSON serializable dict containing information in the following format::

            { 'units' : 'm' // or other unit
              'elevations' : [ ... list of floats ... ] }
        """
        return None

    def get_valid_times(self, **kwargs):
        """ Get valid times for the specified query.
        :param kwargs: All the keyword arguments that would normally be valid for a GetMap request. See ga_ows.common.GetValidTimesMixin.
        :return: A list of datetime objects, preferably in UTC format or None
        """
        return None

    def get_valid_versions(self, group_by=None, **kwargs):
        """ Get valid version strings for the specified query.
        :param group_by: Group version strings by a specified field, such as "time"
        :param kwargs: All the keyword arguments that owuld normally be valid for a GetMap request.  See ga_ows.common.GetValidVersionsMixin.
        :return: A list of the version names or None
        """
        return None

    def layerlist(self):
        """ Get a listing of the valid layer names.
        :return: A list of the valid layer names
        """
        raise NotImplementedError("Must implement layerlist to avoid being abstract")

    def get_2d_dataset(self, layers, srs, bbox, width, height, styles, bgcolor, transparent, time, elevation, v, filter, **kwargs):
        """**REQUIRED**. Get a formatted 2D dataset that can be returned by a GetMap request.

        :param layers: The layers to return.
        :param srs: The spatial reference system to use.  Implementors should handle a PROJ.4 string, SRID, WKT, or EPSG prefaced code.
        :param bbox: The bounding box to use in the **target** spatial reference system as a tuple of (minx, miny, maxx, maxy)
        :param width: The width in pixels of the output
        :param height: The height in pixels of the output
        :param styles: The styles to apply.
        :param bgcolor: The background color to apply to the image
        :param transparent: Whether or not the imsage is transparent
        :param time: The time -parameter to add to the query.
        :param elevation: The elevaltion parameter to add to the query
        :param v: The version parameter to add to the query
        :param filter: A dict object containing the object filter.  Different adapters may implement this differently
        :param kwargs: Any other keyword arguments that are added to the request.  Handled adapter by adapter.
        :return: One of three kind of data: A Cairo Surface object; a Scipy NxNx4-channel array; An osgeo.gdal.Dataset
        """
        raise NotImplementedError("Must implement get_2d_dataset to avoid being abstract")

    def get_feature_info(self, wherex, wherey, layers, callback, format, feature_count, srs, filter):
        """**REQUIRED** Get a formatted feature_info document that can be returned by GetFeatureInfo.

        :param wherex: The X-coordinate in the target reference system.
        :param wherey: The Y coordinate in the target reference system.
        :param layers: The layers to query
        :param callback: A JSONP callback if necessary.
        :param format: The target format to return.  Should at least support "json"
        :param feature_count: A maximum number of features to return per layer.
        :param srs: The spatial reference of the request.
        :param filter: The filter that went into the WMS GetMap request
        :return: A dict containing the feature info results in a JSON seralizable format.
        """
        raise NotImplementedError("Must implement get_feature_info to avoid being abstract")

    def nativesrs(self, layer):
        """**REQUIRED** Get the native SRS for the layer as a WKT string.
        :param layer:
        :return: Text contiaiing the WKT for the layer.
        """
        raise NotImplementedError("Must implement nativesrs to avoid being abstract")

    def nativebbox(self, layer=None):
        """**REQUIRED** for GetCapabilities The bounding box of the layer in the native SRS.
        :return: A tuple or list of (minx, miny, maxx, maxy)
        """
        raise NotImplementedError("Must implement nativebbox to avoid being abstract")

    def styles(self):
        """
        :return: A list of style names valid for the service.
        """
        return self.styles.keys()

    def get_layer_descriptions(self):
        """**REQUIRED** for GetCapabilities.

        This should return a list of dictionaries.  Each dictionary should follow this format::
            { "name" : layer_name,
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
            { "name" : style_name,
              "title" : style_title,
              "legend_width" : style_legend_width,
              "legend_height" : style_legend_height,
              "legend_url" : style_legend_url
            }
        """

        raise NotImplementedError("Must implement to support GetCapabilities")

    def get_service_boundaries(self):
        """**REQUIRED** for GetCapabilities.

        This should return a dictionary containing this::

            { "minx" : west_boundary_epsg4326,
              "miny" : south_boundary_epsg4326,
              "maxx" : east_boundary_epsg4326,
              "maxy" : north_boundary_epsg4326
            }
        """
        raise NotImplementedError("Must implement to support GetCapabilities")



class GetMapMixin(common.OWSMixinBase):
    """ Handle the GetMap request.  This is the central request of WMS.
    """

    #: The Celery-cooked (@task name) subclass of :class:ga_ows.tasks.DeferredRenderer that can be used to distribute
    #: rendering requests.  This is for deferred rendering only.  Leave as None if you want the webserver to handle
    #: WMS requests.
    task = None

    class Parameters(common.CommonParameters):
        layers = utils.MultipleValueField()
        srs = f.CharField(required=False)
        bbox = utils.BBoxField()
        width = f.IntegerField()
        height =f.IntegerField()
        styles = utils.MultipleValueField(required=False)
        format = f.CharField()
        bgcolor = f.CharField(required=False)
        transparent = f.BooleanField(required=False)
        time = f.DateTimeField(required=False)
        filter = f.CharField(required=False)
        elevation = f.FloatField(required=False)
        v = f.CharField(required=False)
        fresh = f.BooleanField(required=False)

        @classmethod
        def from_request(cls, request):
            request['layers'] = request.get('layers').split(',')
            request['srs'] = request.get('srs', None)
            request['filter'] = request.get('filter')
            request['bbox'] = request.get('bbox')
            request['width'] = int( request.get('width') )
            request['height'] = int( request.get('height') )
            request['styles'] = request.get('styles').split(',')
            request['format'] = request.get('format', 'png')
            request['bgcolor'] = request.get('bgcolor')
            request['transparent'] = request.get('transparent', False) == 'true'
            request['time'] = utils.parsetime(request.get('time'))
            request['elevation'] = request.get('elevation', None)
            request['v'] = request.get('v', None)
            request['fresh'] = request.get('fresh', False)

    def GetMap(self, r, kwargs):
        parms = GetMapMixin.Parameters.create(kwargs).cleaned_data

        kwargs = { i : j for i, j in kwargs.items() if i not in parms }

        item = self.adapter.get_cache_record(**parms)
        if item and not parms['fresh']:
            return HttpResponse(item, mimetype='image/'+parms['format'])

        if self.adapter.requires_time and 'time' not in parms:
            raise common.MissingParameterValue.at('time')
        if self.adapter.requires_elevation and 'elevation' not in parms:
            raise common.MissingParameterValue.at('elevation')

        if parms['format'].startswith('image/'):
            fmt = parms['format'][len('image/'):]
        else:
            fmt = parms['format']

        if self.task:
            ret = self.task.delay(parms).get()
        else:
            fltr = None
            if parms['filter']:
                fltr = json.loads(parms['filter'])

            ds = self.adapter.get_2d_dataset(
                layers=parms['layers'],
                srs=parms['srs'],
                bbox=parms['bbox'],
                width=parms['width'],
                height=parms['height'],
                styles=parms['styles'],
                bgcolor=parms['bgcolor'],
                transparent=parms['transparent'],
                time=parms['time'],
                elevation=parms['elevation'],
                v=parms['v'],
                filter = fltr,
                format = fmt.encode('ascii'),
                **kwargs
            )

            tmp = None
            ret = None

            # this codepath is officially confusing.  Here's the deal.  We have several different ways of returning
            # datasets that ga_wms can handle.
            # We can A: return a GDAL dataset.  This will be written to a tempfile and passed to the requestor.
            #
            # B: return a filename.  This is assumed to already be in the proper format.  If it's not, you're going to
            # confuse a bunch of people
            #
            # C: return a numpy array in which case scipy is asked to handle it through "imsave"
            #
            # D: return a file or StringIO instance.  This is also already assumed to be in the proper format
            #
            # All these cases are handled properly by the below code, HOWEVER, as it stands right now if you return
            # filenames, files, or StringIO isntances, we assume that you're caching them yourself.  Otherwise why would
            # you have handed us a real file?

            if not isinstance(ds, gdal.Dataset): # then it == a Cairo imagesurface or numpy array, or at least... it'd BETTER be
                if HAVE_CAIRO and isinstance(ds,cairo.Surface):
                    tmp = tempfile.NamedTemporaryFile(suffix='.png')
                    ds.write_to_png(tmp.name)
                    ds = gdal.Open(tmp.name)
                    # TODO add all the appropriate metadata from the request into the dataset if this == being returned as a GeoTIFF
                elif isinstance(ds, file):
                    ret = ds
                elif isinstance(ds, StringIO):
                    ret = ds

                elif isinstance(ds, basestring):
                    try:
                        ret = open(ds)
                    except IOError:
                        if HAVE_SCIPY:
                            tmp = tempfile.NamedTemporaryFile(suffix='.tif')
                            scipy.misc.imsave(tmp.name, ds)
                            ds = gdal.Open(tmp.name)
                            # TODO add all the appropriate metadata from the request into the dataset if this == being returned as a GeoTIFF
                elif HAVE_SCIPY:
                    tmp = tempfile.NamedTemporaryFile(suffix='.tif')
                    scipy.misc.imsave(tmp.name, ds)
                    ds = gdal.Open(tmp.name)
                    # TODO add all the appropriate metadata from the request into the dataset if this == being returned as a GeoTIFF

            if not ret:
                if fmt == 'tiff' or fmt == 'geotiff':
                    driver = gdal.GetDriverByName('GTiff')
                elif fmt == 'jpg' or fmt == 'jpeg':
                    driver = gdal.GetDriverByName('jpeg')
                elif fmt == 'jp2k' or fmt == 'jpeg2000':
                    tmp = tempfile.NamedTemporaryFile(suffix='.jp2')
                    driver = gdal.GetDriverByName('jpeg2000')
                else:
                    driver = gdal.GetDriverByName(fmt.encode('ascii'))

                try:
                    tmp = tempfile.NamedTemporaryFile(suffix='.' + fmt)
                    ds2 = driver.CreateCopy(tmp.name, ds)
                    del ds2
                    tmp.seek(0)
                    ret = tmp.read()
                    self.adapter.cache_result(ret, **parms)
                except Exception as ex:
                    del tmp
                    raise common.NoApplicableCode(str(ex))

        return HttpResponse(ret, mimetype=fmt)


class GetFeatureInfoMixin(common.OWSMixinBase):
    """ Handle the GetFeatureInfo request in WMS.  Requires that the get_feature_info method is implemented in the adapter.
    """
    class Parameters(common.CommonParameters):
        layers = utils.MultipleValueField()
        bbox = utils.BBoxField()
        width = f.IntegerField()
        height = f.IntegerField()
        i = f.IntegerField()
        j = f.IntegerField()
        srs = f.CharField(required=False)
        callback = f.CharField(required=False)
        format = f.CharField()
        feature_count = f.IntegerField(required=False)
        filter = f.CharField(required=False)

        @classmethod
        def from_request(cls, request):
            request['layers'] = request.get('layers', '').split(',')
            request['bbox'] = request.get('bbox')
            request['width'] = int( request.get('width') )
            request['height'] = int( request.get('height') )
            request['i'] = int( request.get('i', request.get('y')) )
            request['j'] = int( request.get('j', request.get('x')) )
            request['srs'] = request.get('srs', None)
            request['format'] = request.get('format', 'application/json')
            request['callback'] = request.get('callback', None)
            request['filter'] = request.get('filter', None)
            if not request['callback']:
                request['callback'] = request.get('jsonp', None)
            request['feature_count'] = request.get('feature_count', None)

    def GetFeatureInfo(self, r, kwargs):
        parms = GetFeatureInfoMixin.Parameters.create(kwargs).cleaned_data

        y = parms['i']
        x = parms['j']

        bbox = parms['bbox']
        width = parms['width']*1.0
        height = parms['height']*1.0

        wherex = bbox[0] + x/width*(bbox[2]-bbox[0])
        wherey = bbox[1] + (height-y)/height*(bbox[3]-bbox[1])
        if 'filter' in kwargs and kwargs['filter']:
            parms['filter'] = json.loads(kwargs['filter'])
        else:
            parms['filter'] = common.get_filter_params(kwargs)

        for k,v in kwargs.items():
            if k not in parms:
                parms[k.lower()] = v
        info = self.adapter.get_feature_info(wherex, wherey, **parms)

        if parms['callback']:
            return HttpResponse("{callback}({json})".format(callback=parms['callback'], json=json.dumps(info)))
        elif parms['format'] == 'application/json':
            return HttpResponse(json.dumps(info), mimetype='application/json')
        else:
            elt = etree.Element('FeatureInfoResponse')
            for i, layer in enumerate(info.keys()):
                for feature in info[layer]:
                    fields = etree.SubElement(elt, "FIELDS")
                    for k, v in feature.items():
                        fields.set(k, unicode(v))
            
            return HttpResponse(etree.tostring(elt, xml_declaration=True), mimetype='application/vnd.ogc.wms_xml')
            #raise common.OWSException.at('GetFeatureInfo', "Feature info format not supported")

class GetStylesMixin(common.OWSMixinBase):
    """ TODO: Handle the GetStyles request in WMS.
    """


class GetLegendGraphicMixin(common.OWSMixinBase):
    """ TODO: Handle the GetLegendGraphic request in WMS.
    """


class DescribeLayerMixin(common.OWSMixinBase):
    """ TODO: Handle the DescribeLayer request in WMS
    """


class WMS(
    common.OWSView,
    common.GetValidElevationsMixin,
    common.GetValidVersionsMixin,
    common.GetValidTimesMixin,
    GetFeatureInfoMixin,
    GetMapMixin,
    # GetStylesMixin,
    # GetLegendGraphicMixin,
    # DescribeLayerMixin
):
    """
    A Django generic view for handling a WMS service.  The basic WMS service
    contains methods for GetCapabilities, GetMap, and GetFeatureInfo, as well
    as extensions for GetValidTimes and GetValidElevations.

    The key roles of this class are to expose views and parse and validate
    requests.  The actual work behind the views is largely done elsewhere.
    Much of the default WMS view class depends on an adapter class for support.
    The adapter must define several key methods to make a model available for
    serving up as a WMS service.  Adapters should define:

        * requires_time : Boolean.  Whether or not time is a required parameter of the service
        * requires_elevation : Boolean. Whether or not elevation is a required parameter of the service.
        * get_feature_info(version, wherex, wherey, srs, query_layers, info_format, feature_count, exceptions, **kwargs) : HttpResponse. Some kind of feature info response for a given x/y
        * get_wmsconfig() : WMSConfig. For creating the WMSFeatureInfo.  Since the WMSConfig is a fairly heavy object, I recommend only calculating this lazily.
        * get_valid_times(**kwargs) : Get valid times to use in the time field.  Should be a JSON object expressing a list of { value : TIME } and { range : [TIME, TIME] } objects.
        * get_valid_elevations(**kwargs) : Get valid elevations to use in the elevation request field.  Should be a JSON object expressing elevations like this: { units : 'm', 'elevations' : [e1, [e21,e22], e3, e4, ...]
        * nativebbox() : Get the native bounding box of the data.
        * nativesrs(layer) : Get the native SRS of the a layer
        * layerlist() : Get a list of all layers.
        * styles() : Get a list of available stylesheets
        * get_2d_dataset(bbox, width, height, query_layers, styles = None, **args): GDAL dataset or Cairo surface.  Return a rendered image of the data.

    """

    #: The WMSAdapter subclass assigned to this view.  This is **required**.
    adapter = None

    #: This will probably go away in favor of a more general solution.  A list of requests that this service accepts.
    #:
    #: Requests is already pre-set for you, but if you derive a new class from WMS, you may need to add new operations
    #: to it.  If you do so, you should append dictionaries of the format::
    #:     { "name" : "{{ the request name }}",
    #:       "formats" : [ a list of formats that can be returned in the response ] }
    requests = [
        { "name" : "GetMap", "formats" : []},
        { "name" : "GetFeatureInfo", "formats" : ['json','text/plain','text/html']},
        { "name" : "GetValidTimes", "formats" : ['json']},
        { "name" : "GetValidVersions", "formats" : ['json']},
        { "name" : "GetValidTimes", "formats" : ['json']},
    ]

    #: The title of the service
    title = "Geoanalytics WMS"

    #: The name of a contact person for information about the service
    contact_person = None

    #: The name of the contact organization
    contact_organization = None

    #: The name of the contact position
    contact_position = None

    #: The type of the contact address: like "home" "work" "business" etc
    contact_address_type = None

    #: Street address
    contact_address = None

    #: City
    contact_city = None

    #: State (if in the US)
    contact_state = None

    #: Postcode
    contact_postcode = None

    #: Country
    contact_country = None

    #: Email address
    contact_email = None

    #: Metadata keywords as a list
    keywords = []

    #: Fees associated with using the service
    fees = None

    #: Constraints on service usage
    constraints = None

    def get_capabilities_response(self, request, req):
        context = {
            "title" : self.title,
            "contact_person" : self.contact_person,
            "contact_organization" : self.contact_organization,
            "contact_position" : self.contact_position,
            "contact_address_type" : self.contact_address_type,
            "contact_address" : self.contact_address,
            "contact_city" : self.contact_city,
            "contact_state" : self.contact_state,
            "contact_postcode" : self.contact_postcode,
            "contact_country" : self.contact_country,
            "contact_email" : self.contact_email,
            "service_url" : request.build_absolute_uri(),
            "keywords" : self.keywords,
            "fees" : self.fees,
            "constraints" : self.constraints,
            "layers" : self.adapter.get_layer_descriptions(),
            "service_bounds" : self.adapter.get_service_boundaries()
        }

        return render_to_response('ga_ows/WMS_Capabilities.template.xml', context)



