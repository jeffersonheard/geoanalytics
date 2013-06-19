from tastypie.api import Api
from tastypie.fields import ForeignKey, ManyToManyField, OneToOneField
from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization

from ga_resources import models
from django.contrib.auth import models as auth


class AbstractPageResource(ModelResource):
    """Abstract class that provides sensible defaults for creating new pages via the RESTful API. e.g. unless there's
     some specific value passed in for whether or not the page should show up in the header, footer, and sidebar, we
     want to dehydrate that field specifically"""

    def _dehydrate_with_default(self, bundle, datum, default):
        if datum not in bundle.data or bundle.data[datum] is None:
            return default

    def dehydrate_in_menus(self, bundle):
        return self._dehydrate_with_default(bundle, 'in_menus', False)

    def dehydrate_requires_login(self, bundle):
        return self._dehydrate_with_default(bundle, 'requires_login', False)

    def dehydrate_in_sitemap(self, bundle):
        return self._dehydrate_with_default(bundle, 'in_sitemap', False)


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


class AncillaryResource(AbstractPageResource):
    class Meta(BaseMeta):
        queryset = models.AncillaryResource.objects.all()
        resource_name = "ancillary"

class SpatialMetadata(ModelResource):
    class Meta:
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        allowed_methods = ['get']
        queryset = models.SpatialMetadata.objects.all()
        resource_name = 'spatial_metadata'


class DataResource(AbstractPageResource):
    spatial_metadata = OneToOneField(SpatialMetadata, 'spatial_metadata', full=True, null=True, blank=True, readonly=True)

    class Meta(BaseMeta):
        queryset = models.DataResource.objects.all()
        resource_name = 'data'
        fields = ['title','status','content','resource_file','resource_url','resource_irods_file','kind','driver']


class ResourceGroup(AbstractPageResource):
    class Meta(BaseMeta):
        queryset = models.ResourceGroup.objects.all()
        resource_name = "resource_group"

resources = Api()
resources.register(User())
resources.register(Group())
resources.register(AncillaryResource())
resources.register(SpatialMetadata())
resources.register(DataResource())
resources.register(ResourceGroup())


class Style(AbstractPageResource):
    class Meta(BaseMeta):
        queryset = models.Style.objects.all()
        resource_name = "style"

styles = Api()
styles.register(Style())


class RenderedLayer(AbstractPageResource):
    data_resource = ForeignKey(DataResource, 'data_resource')
    default_style = ForeignKey(Style, 'default_style', related_name='default_for_layer')
    styles = ManyToManyField(Style, 'styles')

    class Meta(BaseMeta):
        queryset = models.RenderedLayer.objects.all()
        resource_name = 'rendered_layer'


layers = Api()
layers.register(RenderedLayer())
