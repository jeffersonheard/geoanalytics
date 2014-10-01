#!/usr/bin/env python
import os, sys

if __name__ == "__main__":
    os.environ.setdefault('PYTHONPATH', '/home/docker/geoanalytics')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoanalytics.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

