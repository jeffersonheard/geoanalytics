from django.contrib.gis.db import models
from mezzanine.pages.models import Page, RichText

class Application(Page, RichText):
    WMS = 0
    GOOGLE_ROADS = 1
    GOOGLE_HYBRID = 2
    GOOGLE_SATELLITE = 3
    OSM = 4
    BING_ROADS = 5
    BING_AERIAL = 6
    NONE = -1

    default_base_map = models.PositiveSmallIntegerField(choices=(
        (WMS, "Web Map Service"),
        (GOOGLE_ROADS, "Google Roads"),
        (GOOGLE_HYBRID, "Google Hybrid"),
        (GOOGLE_SATELLITE,"Google Satellite"),
        (OSM, "Open Streetmaps"),
        (BING_ROADS, "Bing Roads"),
        (BING_AERIAL, "Bing Aerial"),
        (NONE, "No Basemap"),
    ))

    script_tags = models.TextField(blank=True)
    link_tags = models.TextField(blank=True)
    application_script = models.FileField(upload_to="applications", null=True, blank=True)
    application_css = models.FileField(upload_to="applications", null=True, blank=True)
    renderedlayers = models.ManyToManyField(through="ApplicationLayer", blank=True, to='ga_resources.RenderedLayer')
    default_includes = models.BooleanField(default=True)

class ApplicationLayer(models.Model):
    application = models.ForeignKey(Application)
    renderedlayer = models.ForeignKey("ga_resources.RenderedLayer")
    weight = models.IntegerField(default=0)

    class Meta:
        ordering = ("-weight",)