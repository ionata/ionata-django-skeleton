"""Storage classes for the project."""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from storages.backends import s3boto3


class StaticS3(s3boto3.S3Boto3Storage):  # pylint: disable=abstract-method
    """The static storage for the project."""

    location = settings.STATIC_URL.lstrip("/")


class MediaS3(s3boto3.S3Boto3Storage):  # pylint: disable=abstract-method
    """The default_storage for the project."""

    location = settings.MEDIA_URL.lstrip("/")

    def create_bucket(self):
        """Ensure the bucket exists when in debug.

        This method has been copied and edited from django-storages v1.9.1
        storages.backend.s3boto3.S3Boto3Storage._get_or_create_bucket.
        """
        if not settings.DEBUG:
            raise ImproperlyConfigured(
                "Buckets can only be created when `DEBUG = True`."
            )
        name = self.bucket_name
        bucket = self.connection.Bucket(name)
        try:
            # Directly call head_bucket instead of bucket.load() because head_bucket()
            # fails on wrong region, while bucket.load() does not.
            bucket.meta.client.head_bucket(Bucket=name)
        except s3boto3.ClientError as err:
            if err.response["ResponseMetadata"]["HTTPStatusCode"] == 301:
                raise ImproperlyConfigured(
                    f"Bucket {name} exists, but in a different "
                    "region than we are connecting to. Set "
                    "the region to connect to by setting "
                    "AWS_S3_REGION_NAME to the correct region."
                )

            if err.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
                # Notes: When using the us-east-1 Standard endpoint, you can create
                # buckets in other regions. The same is not true when hitting region specific
                # endpoints. However, when you create the bucket not in the same region, the
                # connection will fail all future requests to the Bucket after the creation
                # (301 Moved Permanently).
                #
                # For simplicity, we enforce in S3Boto3Storage that any auto-created
                # bucket must match the region that the connection is for.
                #
                # Also note that Amazon specifically disallows "us-east-1" when passing bucket
                # region names; LocationConstraint *must* be blank to create in US Standard.
                bucket_params = {}
                region_name = self.connection.meta.client.meta.region_name
                if region_name != "us-east-1":
                    bucket_params["CreateBucketConfiguration"] = {
                        "LocationConstraint": region_name
                    }
                bucket.create(**bucket_params)
            else:
                raise
        return bucket
