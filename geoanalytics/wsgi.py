from __future__ import unicode_literals

import os

os.environ.setdefault('PYTHONPATH', '/home/docker/geoanalytics/geoanalytics')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

