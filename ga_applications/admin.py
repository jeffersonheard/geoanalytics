from django.contrib import admin
from mezzanine.pages import admin as pages_admin
from .models import *

#class LayersInline(admin.TabularInline):
#    model = ApplicationLayer
#    extra = 1

#class ApplicationAdmin(pages_admin.PageAdmin):
#    inlines = (LayersInline,)

admin.site.register(Application, admin.ModelAdmin)
admin.site.register(ApplicationLayer, admin.ModelAdmin)