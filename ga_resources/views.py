from ga_ows.views import wfs, wms
from ga_resources import models, drivers

import importlib

class WMSAdapter(wms.WMSAdapterBase):
    #def get_cache_record(self, layers, srs, bbox, width, height, styles, format, bgcolor, transparent, time, elevation, v, filter, **kwargs):
    #    """see if we already have a cache entry prepared and if so read and return it"""

    def layerlist(self):
        return [l.slug for l in models.RenderedLayer.objects.all()]

    def get_2d_dataset(self, layers, srs, bbox, width, height, styles, bgcolor, transparent, time, elevation, v, filter, **kwargs):
        """use the driver to render a tile"""
        return open(drivers.render(kwargs['format'], width, height, bbox, srs, styles, layers))

    def get_feature_info(self, wherex, wherey, layers, callback, format, feature_count, srs, filter):
        """use the driver to get feature info"""
        return {} # FIXME write this as soon as possible

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
        layers = models.RenderedLayer.objects.all()
        ret = []
        for layer in layers:
            desc = {}
            ret.append(desc)
            desc['name'] = layer.slug
            desc['title'] = layer.title
            desc['srs'] = layer.data_resource.spatial_metadata.native_srs
            desc['queryable'] = True
            desc['minx'], desc['miny'], desc['maxx'], desc['maxy'] = layer.data_resource.native_bounding_box.extent  # FIXME this is not native
            desc['ll_minx'], desc['ll_miny'], desc['ll_maxx'], desc['ll_maxy'] = layer.data_resource.bounding_box.extent
            desc['styles'] = []
            desc['styles'].append({
                'name' : layer.default_style.slug,
                'title' : layer.default_style.title,
                'legend_width' : layer.default_style.legend_width,
                'legend_height' : layer.default_style.legend_height,
                'legend_url' : layer.default_style.legend.url if layer.default_style.legend else ""
            })
            for style in layer.styles.all():
                desc['styles'].append({
                    'name' : style.slug,
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
