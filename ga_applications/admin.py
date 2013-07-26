from django.contrib import admin
#from mezzanine.pages import admin as pages_admin
from .models import *

class LayersInline(admin.TabularInline):
    model = ApplicationLayer
    extra = 1

class ApplicationAdmin(admin.ModelAdmin):
    inlines = (LayersInline,)

admin.site.register(Application, ApplicationAdmin)
#admin.site.register(ApplicationLayer, admin.ModelAdmin)