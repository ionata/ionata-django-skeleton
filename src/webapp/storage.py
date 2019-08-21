from django.conf import settings
from storages.backends import s3boto3


class StaticS3(s3boto3.S3Boto3Storage):  # pylint: disable=abstract-method
    location = settings.STATIC_URL.lstrip("/")


class MediaS3(s3boto3.S3Boto3Storage):  # pylint: disable=abstract-method
    location = settings.MEDIA_URL.lstrip("/")
