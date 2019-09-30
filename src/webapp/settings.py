"""Settings for your application."""
from typing import Any, List, Optional, Tuple, Type, Dict
from urllib.parse import urlparse

from environ import Env

env = Env()

# Bootstrap debug
DEBUG = env.bool("DEBUG")

default_databse_url = env.NOTSET

scheme: Dict[str, Tuple[Type, Any]] = {"CELERY_BROKER_URL": (str, "redis://")}

if DEBUG:
    default_databse_url = "postgres://django:django@db:5432/django"
    scheme = {
        **scheme,
        **{
            "CELERY_BROKER_URL": (str, "redis://redis"),
            "ADMIN_USER": (dict, {"email": "test@example.com", "password": "password"}),
            "AWS_STORAGE_BUCKET_NAME": (str, "django"),
            "AWS_S3_REGION_NAME": (str, ""),
            "AWS_S3_SECURE_URLS": (bool, True),
            "MAILGUN_API_KEY": (str, ""),
            "CELERY_TASK_DEFAULT_QUEUE": (str, "celery"),
        },
    }

env = Env(**scheme)

# Core
# TODO: set the PROJECT_NAME setting - do not include spaces in this name
PROJECT_NAME: str = "<INSERT_PROJECT_NAME_HERE>"
SECRET_KEY: str = env("SECRET_KEY")
SITE_URL: str = env("SITE_URL")

url = urlparse(SITE_URL)

ADMINS: List[Tuple[str, str]] = [("webmaster", "webmaster@ionata.com.au")]
MANAGERS = ADMINS
ADMIN_USER = env.dict("ADMIN_USER")
ALLOWED_HOSTS: List[str] = [url.netloc]
CORS_ORIGIN_WHITELIST: List[str] = [SITE_URL]
HEARTBEAT_SERVER: Optional[str] = "https://heartbeat.ionata.com.au"


# Services
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_TASK_DEFAULT_QUEUE = env.str("CELERY_TASK_DEFAULT_QUEUE")
DATABASES = {"default": env.db_url(default=default_databse_url)}

# Storage
DEFAULT_FILE_STORAGE = "webapp.storage.MediaS3"
STATICFILES_STORAGE = "webapp.storage.StaticS3"

AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")

INSTALLED_APPS = [
    # Project apps
    "webapp",
    "users",
    # Our defaults
    "corsheaders",
    "anymail",
    "django_extensions",
    "storages",
    "django_celery_beat",
    "django_celery_results",
    # Core django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

ROOT_URLCONF = "webapp.urls"
WSGI_APPLICATION = "webapp.wsgi.application"
SITE_ID = 1

# i18n
LANGUAGE_CODE = "en-AU"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Auth
ANONYMOUS_USER_ID = -1
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
AUTH_USER_MODEL = "users.User"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Security
INTERNAL_IPS = ["127.0.0.1"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_PATH = "/backend/"
CSRF_COOKIE_PATH = "/backend/"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
AWS_AUTO_CREATE_BUCKET = False
AWS_DEFAULT_ACL = "private"
AWS_BUCKET_ACL = "private"

# URLs
MEDIA_URL = "/assets/media/"
STATIC_URL = "/assets/static/"

# Celery
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}  # 1 hour.
CELERY_RESULT_BACKEND = "django-db"
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_APP_NAME = PROJECT_NAME

# Email
EMAIL_SUBJECT_PREFIX = f"[Django - {PROJECT_NAME}] "
DEFAULT_FROM_EMAIL = f"no-reply@{url.hostname}"
SERVER_EMAIL = f"no-reply@{url.hostname}"
MAILGUN_SENDER_DOMAIN = env("MAILGUN_SENDER_DOMAIN", default=f"mailgun.{url.hostname}")
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
MAILGUN_API_KEY = env("MAILGUN_API_KEY")

# Misc
FRONTEND_URL = SITE_URL

# DRF Core
LOGIN_URL = "/backend/api/v1/login/"
LOGIN_REDIRECT_URL = "/backend/api/v1/"
INSTALLED_APPS += [
    "rest_framework",
    "rest_framework.authtoken",
    "rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "rest_auth.registration",
    "django_filters",
]
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework_filters.backends.RestFrameworkFilterBackend"
    ],
}

# DRF Auth
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_REGISTRATION = "enabled"
REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "users.serializers.UserDetailsSerializer",
    "PASSWORD_RESET_SERIALIZER": "users.serializers.PasswordResetSerializer",
    "LOGIN_SERIALIZER": "users.serializers.LoginSerializer",
}
REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": "users.serializers.RegisterSerializer"
}

if DEBUG:
    ALLOWED_HOSTS = ["*"]
    ADMINS = []
    MANAGERS = ADMINS

    # Storage
    AWS_S3_REGION_NAME = ""
    AWS_S3_ENDPOINT_URL = "http://minio:9000"
    AWS_ACCESS_KEY_ID = "djangos3"
    AWS_SECRET_ACCESS_KEY = "djangos3"
    AWS_S3_SECURE_URLS = env("AWS_S3_SECURE_URLS")
    AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default=url.netloc)
    HEARTBEAT_SERVER = None

    # Core
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

    # Security
    CORS_ORIGIN_ALLOW_ALL = True
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    AWS_AUTO_CREATE_BUCKET = True

    # Email
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # CORS
    CORS_ORIGIN_WHITELIST = [item for item in ALLOWED_HOSTS if item != "*"]

# Post debug setup dependant settings
CSRF_TRUSTED_ORIGINS = CORS_ORIGIN_WHITELIST