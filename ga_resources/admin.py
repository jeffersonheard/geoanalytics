from copy import deepcopy
from mezzanine.pages.admin import PageAdmin
from django.contrib.gis import admin
from ga_resources.models import *

# TODO add prepopulated fields to all models with slug fields.
# class ArticleAdmin(admin.ModelAdmin):
#   prepopulated_fields = {"slug": ("title",)}


#class OSMPageAdmin(admin.OSMGeoAdmin):
#    fieldsets = deepcopy(PageAdmin.fieldsets)

#class DataResourceAdmin(admin.OSMGeoAdmin):
#    fieldsets = deepcopy(PageAdmin.fieldsets) + ((None, {"fields" : (
#        'content',
#        "resource_file", "resource_url", "resource_irods_env", "resource_irods_file",
#        "time_represented","perform_caching","cache_ttl","data_cache","bounding_box","kind","driver"
#    )}),)

admin.site.register(CatalogPage, PageAdmin)
#admin.site.register(Verb, PageAdmin)
admin.site.register(DataResource, PageAdmin)
admin.site.register(ResourceGroup, PageAdmin)
admin.site.register(OrderedResource)

admin.site.register(AncillaryResource, PageAdmin)

admin.site.register(RenderedLayer, PageAdmin)
admin.site.register(Style, PageAdmin)
