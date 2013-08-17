from django.conf.urls import patterns, url, include
from ga_resources import api, views, signals

urlpatterns = patterns('',
    url(r'^resources/', include(api.resources.urls)),
    url(r'^styles/', include(api.styles.urls)),
    url(r'^layers/', include(api.layers.urls)),
    url(r'^wms/', views.WMS.as_view()),
    url(r'^wfs/', views.WFS.as_view()),
    url(r'^download/(?P<slug>.*)$', views.download_file),
    url(r'^createpage/', views.create_page),
    url(r'^deletepage/', views.delete_page),
    url(r'^extent/(?P<slug>.*)/', views.extent),
)
