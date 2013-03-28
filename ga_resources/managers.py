"""
Without this file and these classes, the search function 500s on any geographic resources.  All pages that are
also GeoDjango models should use a GeoPageManager instead of a GeoManager
"""

from mezzanine.pages.managers import PageManager
from mezzanine.core.managers import SearchableQuerySet
from django.contrib.gis.db.models import GeoManager
from django.contrib.gis.db.models.query import GeoQuerySet

class SearchableGeoQuerySet(SearchableQuerySet, GeoQuerySet):
    def __init__(self, model, using=None, search_fields=None, **kwargs):
        SearchableQuerySet.__init__(self, model, search_fields=search_fields, **kwargs)
        GeoQuerySet.__init__(self, model, using=self._db)

class GeoPageManager(GeoManager, PageManager):
    """a combined manager for geo and pages.  this must be used to make the search function work."""

    def get_query_set(self):
        search_fields = self._search_fields
        return SearchableGeoQuerySet(self.model, using=self._db, search_fields=search_fields)