from django.conf.urls import patterns, url, include
from ga_resources import api, views

urlpatterns = patterns('',
    url(r'^resources/', include(api.resources.urls)),
    url(r'^styles/', include(api.styles.urls)),
    url(r'^layers/', include(api.layers.urls)),
    url(r'^wms/', views.WMS.as_view()),
)