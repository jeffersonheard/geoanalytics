DEBUG = True
LOCAL = True

# Make these unique, and don't share it with anybody.
SECRET_KEY = "68577c40-bb5b-434b-9394-6b85e307682dfa6e82ef-84bf-45bf-9ed1-c291ce6f263b59ec94f3-3021-476c-b75e-1a59f1de6cde"
NEVERCACHE_KEY = "c2a46c2f-566e-42b4-988d-7dfa23f75aff05a354d4-d3ef-4784-abbf-6c8371ccff6050f29287-c354-4046-8013-ba0d75f5ed93"

if not LOCAL:
    AWS_SECRET_ACCESS_KEY = ""
    AWS_ACCESS_KEY_ID = ""
    AWS_STORAGE_BUCKET_NAME = "" 
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    STATIC_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'grappelli/'

