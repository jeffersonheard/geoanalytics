from django.contrib.gis import admin
from ga_resources.models import *

# TODO add prepopulated fields to all models with slug fields.
# class ArticleAdmin(admin.ModelAdmin):
#   prepopulated_fields = {"slug": ("title",)}

admin.site.register(AncillaryResource)
admin.site.register(DataResource)
admin.site.register(LayerGroup)
admin.site.register(Style)
admin.site.register(StyleTemplate)
admin.site.register(StyleTemplateVariable)
admin.site.register(WCSLayer)
admin.site.register(WFSLayer)
admin.site.register(WMSLayer)
admin.site.register(WMTSLayer)
admin.site.register(WMVSLayer)
admin.site.register(SOSLayer)

