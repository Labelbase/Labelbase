import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from .mysentry import before_send


from pathlib import Path
from configparser import RawConfigParser

# Build paths inside the project like this: BASE_DIR / 'subdir'.
PROJECT_PATH = BASE_DIR = Path(__file__).resolve().parent.parent

proj_config = RawConfigParser()
config_file_path = "{}/config.ini".format(PROJECT_PATH)
try:
    if proj_config.read(config_file_path) == []:
        from .make_config import generate_config_file
        if not os.path.isfile(config_file_path):
            print("creating config file, here: {}".format(config_file_path))
            generate_config_file(config_file_path)
            assert proj_config.read(config_file_path) == []
except AssertionError:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        "Configuration file {} not found!".format(config_file_path)
    )

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = proj_config.get("internal", "secret_key")
CRYPTOGRAPHY_SALT = proj_config.get("internal", "crypto_salt")

DEBUG = proj_config.getboolean("internal", "debug")

SELF_HOSTED = proj_config.getboolean("internal", "self_hosted", fallback=True)
if DEBUG:
    ALLOWED_HOSTS = ["*"] # we don't know your host config, keep like that at the moment.
else:
    ALLOWED_HOSTS = [proj_config.get("internal", "allowed_host")]

#SENTRY_DSN = "https://3b833ae08ccc4ff68793e961fff4921c@o4504646963232768.ingest.sentry.io/4504646967361536"

SENTRY_DSN = proj_config.get("internal", "sentry_dsn")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    #integrations=[
    #    DjangoIntegration(),
    #],
    before_send=before_send,
    traces_sample_rate=1.0,
    send_default_pii=True, # must be "True" here, will skip or omit in `before_send` callback
)
sentry_sdk.set_tag("version", "2.2.3")


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': './labelbase.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,  # Keep 5 backup files
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'labelbase': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'django.security.DisallowedHost': {
        'handlers': ['null'],
        'propagate': False,
    },
}

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    # 'django.contrib.sessions', # NOTE: We use "user_sessions"
    "user_sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "two_factor",
    "two_factor.plugins.phonenumber",
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",

    "labelbase",
    "userprofile",
    "notifications",

    "bootstrapform",
    "cryptography",
    "rest_framework",
    "rest_framework.authtoken",
    "sekizai",
    "importer",
    "finances",
    "background_task",
    "connectrum",
    "knowledge_base",
    "hashtags",
    "statusapp",
    "attachments",
    "messages_extends",

]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    # "django.middleware.cache.FetchFromCacheMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "threadlocals.middleware.ThreadLocalMiddleware",


]

MESSAGE_STORAGE = 'messages_extends.storages.FallbackStorage'


ROOT_URLCONF = "labellabor.urls"

LOGIN_URL = "two_factor:login"

LOGIN_REDIRECT_URL = "two_factor:profile"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_PATH, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                "statusapp.context_processors.latest_status_message",
            ],
        },
    },
]


CURRENCIES = ['USD', 'EUR', 'GBP', 'CAD', 'CHF', 'AUD', 'JPY']


WSGI_APPLICATION = "labellabor.wsgi.application"

TWO_FACTOR_REMEMBER_COOKIE_AGE = 60 * 60 * 24 * 14


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": proj_config.get("database", "name"),
        "USER": proj_config.get("database", "user"),
        "OPTIONS": {"charset": "utf8mb4"},
        "PASSWORD": proj_config.get("database", "password"),
        'HOST': proj_config.get("database", "host", fallback="labelbase_mysql"),
        'PORT': int(proj_config.get("database", "port", fallback="3306")),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

TWO_FACTOR_WEBAUTHN_RP_NAME = "labelbase.space"

SESSION_ENGINE = "user_sessions.backends.db"

REST_FRAMEWORK = {"DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema"}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')


FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # Up to 100 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # Up to 100 MB
DELETE_ATTACHMENTS_FROM_DISK = True
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-FILE_UPLOAD_HANDLERS
FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]
