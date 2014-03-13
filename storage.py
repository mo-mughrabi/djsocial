"""
    storage.py can be used with amazon S3 storage, it helps in separating between public assets and public media
"""
from __future__ import absolute_import
from django.conf import settings
from storages.backends.s3boto import S3BotoStorage


class S3StaticBucket(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        kwargs['secure_urls'] = False
        kwargs['location'] = 'static/'
        super(S3StaticBucket, self).__init__(*args, **kwargs)