from tastypie.api import Api
from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization

from ga_resources import models
from ga_irods import models as irods
from django.contrib.auth import models as auth


class BaseMeta(object):
    allowed_methods = ['get', 'put', 'post', 'delete']
    authorization = Authorization()
    authentication = ApiKeyAuthentication()


class Group(ModelResource):
    class Meta:
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        allowed_methods = ['get']
        queryset = auth.Group.objects.all()
        resource_name = "group"


class User(ModelResource):
    class Meta:
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        allowed_methods = ['get']
        queryset = auth.User.objects.all()
        resource_name = "user"


class RodsEnvironment(ModelResource):
    class Meta:
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        allowed_methods = ['get']
        queryset = irods.RodsEnvironment.objects.all()
        resource_name = "irods_environment"


class AncillaryResource(ModelResource):
    class Meta(BaseMeta):
        queryset = models.AncillaryResource.objects.all()
        resource_name = "ancillary"


class DataResource(ModelResource):
    class Meta(BaseMeta):
        queryset = models.DataResource.objects.all()
        resource_name = 'data'


class ResourceGroup(ModelResource):
    class Meta(BaseMeta):
        queryset = models.ResourceGroup.objects.all()
        resource_name = "resource_group"

resources = Api()
resources.register(User())
resources.register(Group())
resources.register(RodsEnvironment())
resources.register(AncillaryResource())
resources.register(DataResource())
resources.register(ResourceGroup())


class Style(ModelResource):
    class Meta(BaseMeta):
        queryset = models.Style.objects.all()
        resource_name = "style"


class VectorStyleTemplate(ModelResource):
    class Meta(BaseMeta):
        queryset = models.StyleTemplate.objects.all()
        resource_name = "template"


class VectorStyleTemplateVariable(ModelResource):
    class Meta(BaseMeta):
        queryset = models.StyleTemplateVariable.objects.all()
        resource_name = "variable"

styles = Api()
styles.register(Style())
styles.register(VectorStyleTemplate())
styles.register(VectorStyleTemplateVariable())


class LayerGroup(ModelResource):
    class Meta(BaseMeta):
        queryset = models.LayerGroup.objects.all()
        resource_name = "layer_group"


class SOSLayer(ModelResource):
    class Meta(BaseMeta):
        queryset = models.SOSLayer.objects.all()
        resource_name = "sos"


class WCSLayer(ModelResource):
    class Meta(BaseMeta):
        queryset = models.WCSLayer.objects.all()
        resource_name = "wcs"


class WFSLayer(ModelResource):
    class Meta(BaseMeta):
        queryset = models.WFSLayer.objects.all()
        resource_name = "wfs"


class WMSLayer(ModelResource):
    class Meta(BaseMeta):
        queryset = models.WMSLayer.objects.all()
        resource_name = "wms"


class WMVSLayer(ModelResource):
    class Meta(BaseMeta):
        queryset = models.WMSLayer.objects.all()
        resource_name = "wmvs"


class WMTSLayer(ModelResource):
    class Meta(BaseMeta):
        queryset = models.WMTSLayer.objects.all()
        resource_name = "wmts"

layers = Api()
layers.register(LayerGroup())
layers.register(SOSLayer())
layers.register(WCSLayer())
layers.register(WFSLayer())
layers.register(WMSLayer())
layers.register(WMVSLayer())
layers.register(WMTSLayer())
