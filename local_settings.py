#############
# DATABASES #
#############

# DATABASES = {
#     "default": {
#         # Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
#         "ENGINE": "django.contrib.gis.db.backends.spatialite",
#         # DB name or path to database file if using sqlite3.
#         "NAME": "/home/th/geoanalytics/ga_cms.sql3",
#         # Not used with sqlite3.
#         "USER": "",
#         # Not used with sqlite3.
#         "PASSWORD": "",
#         # Set to empty string for localhost. Not used with sqlite3.
#         "HOST": "",
#         # Set to empty string for default. Not used with sqlite3.
#         "PORT": "",
#     }
# }


DATABASES = {
    "default": {
        # Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        # DB name or path to database file if using sqlite3.
        "NAME": "geoanalytics",
        # Not used with sqlite3.
        "USER": "geoanalytics",
        # Not used with sqlite3.
        "PASSWORD": "geoanalytics",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}


